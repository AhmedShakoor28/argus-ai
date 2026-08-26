"""
Argus-AI Orchestrator
----------------------
Chains DetectionAgent -> VerificationAgent -> ResponseAgent -> ReportAgent
into a single pipeline.

Usage:
    python src/main.py --image path/to/image.jpg --city Rawalpindi

Flow:
    1. Run detection on the image (fire + landslide).
    2. For each disaster type that actually triggered (fire boxes found,
       or landslide classified positive), run verification against
       weather + news for the given city.
    3. Feed each (detection, verification) pair into the Response Agent
       to get a grounded recommendation.
    4. Render the combined report as a PDF via the Report Agent.
    5. Return one combined JSON report covering everything that triggered.

If nothing triggers, the pipeline short-circuits and reports "no disaster
detected" without wasting API calls on verification/response (a PDF is
still generated, noting nothing was detected).

Mutual suppression:
    Fire and landslide co-occurring on the SAME image is rare in reality.
    If fire fires AND landslide fires on the same image, landslide is
    flagged as "suspect" and its final status is decided by the
    verification agent's plausibility check (e.g. no recent rain =
    landslide implausible), not by the classifier's raw confidence alone.
"""

import argparse
import json
import os
import sys
from datetime import datetime

from detection_agent import DetectionAgent
from verification_agent import VerificationAgent
from response_agent import ResponseAgent
from report_agent import ReportAgent

# Confidence threshold below which a fire detection is ignored
FIRE_CONFIDENCE_THRESHOLD = 0.4

# Base confidence threshold for landslide to trigger at all
LANDSLIDE_CONFIDENCE_THRESHOLD = 0.6

# If fire ALSO triggered on the same image, landslide must clear this much
# higher bar to still be treated as a straightforward positive. Below it
# (or even above it, since flags are set regardless of this bar when fire
# co-fires), it's flagged as suspect and verification gets the final say.
LANDSLIDE_SUPPRESSION_THRESHOLD = 0.995

# Default folder where auto-generated PDF reports are saved
DEFAULT_REPORTS_DIR = "reports"


def get_triggered_types(detection_report):
    """
    Inspect a DetectionAgent report and decide which disaster types
    actually warrant verification + response.

    Returns (triggered, flags) where:
      - triggered is a list like ["fire"], ["landslide"], ["fire", "landslide"], or []
      - flags is a dict mapping disaster_type -> list of caution notes
        (e.g. landslide flagged as suspect because fire also fired)
    """
    triggered = []
    flags = {}
    detections = detection_report.get("detections", {})

    fire_detections = detections.get("fire", [])
    fire_triggered = any(d["confidence"] >= FIRE_CONFIDENCE_THRESHOLD for d in fire_detections)
    if fire_triggered:
        triggered.append("fire")

    landslide_result = detections.get("landslide", {})
    landslide_confidence = landslide_result.get("confidence", 0)
    landslide_is_landslide = landslide_result.get("class") == "Landslide"

    if landslide_is_landslide and landslide_confidence >= LANDSLIDE_CONFIDENCE_THRESHOLD:
        triggered.append("landslide")
        if fire_triggered:
            flags["landslide"] = [
                f"Suspect: fire also detected on same image (co-occurrence is rare); "
                f"landslide confidence {landslide_confidence:.3f} "
                f"(suppression bar: {LANDSLIDE_SUPPRESSION_THRESHOLD}); "
                f"final status decided by verification plausibility, not confidence alone."
            ]

    return triggered, flags


def _default_pdf_path(image_path, reports_dir):
    """Build a timestamped PDF filename from the input image name."""
    os.makedirs(reports_dir, exist_ok=True)
    base = os.path.splitext(os.path.basename(str(image_path)))[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(reports_dir, f"{base}_{timestamp}.pdf")


def run_pipeline(image_path, city, fire_model_path, landslide_model_path,
                  mode="both", reports_dir=DEFAULT_REPORTS_DIR, generate_pdf=True):
    """
    Runs the full Detection -> Verification -> Response -> Report pipeline
    for one image. Returns a single combined report dict (with a
    "pdf_path" key added if a PDF was generated).
    """
    print(f"[1/4] Running detection on {image_path} ...")
    detection_agent = DetectionAgent(fire_model_path, landslide_model_path)
    detection_report = detection_agent.analyze(image_path, mode=mode)

    triggered_types, flags = get_triggered_types(detection_report)

    final_report = {
        "image": image_path,
        "city": city,
        "detection": detection_report,
        "triggered_types": triggered_types,
        "results": {}
    }

    if not triggered_types:
        print("No disaster detected above threshold — skipping verification and response.")
        final_report["status"] = "no_disaster_detected"
        if generate_pdf:
            print("[4/4] Generating PDF report ...")
            pdf_path = _default_pdf_path(image_path, reports_dir)
            ReportAgent().generate(final_report, pdf_path)
            final_report["pdf_path"] = pdf_path
            print(f"      -> Saved: {pdf_path}")
        return final_report

    print("[2/4] Initializing verification + response agents ...")
    verification_agent = VerificationAgent()
    response_agent = ResponseAgent()

    for disaster_type in triggered_types:
        print(f"      -> Verifying '{disaster_type}' near {city} ...")
        verification_report = verification_agent.verify(detection_type=disaster_type, city=city)

        is_suspect = disaster_type in flags
        is_plausible = verification_report.get("plausible", True)

        # Gating: a detection flagged as suspect (mutual suppression) AND
        # that fails verification gets downgraded instead of reported as
        # a confirmed disaster.
        if is_suspect and not is_plausible:
            result_status = "unconfirmed"
        elif is_suspect:
            result_status = "suspect_but_plausible"
        else:
            result_status = "confirmed"

        print(f"      -> Generating response recommendation for '{disaster_type}' ...")
        response = response_agent.generate_response(detection_report, verification_report)

        final_report["results"][disaster_type] = {
            "result_status": result_status,
            "caution_flags": flags.get(disaster_type, []),
            "verification": verification_report,
            "response": response
        }

    final_report["status"] = "completed"
    print("[3/4] Verification + response complete.")

    if generate_pdf:
        print("[4/4] Generating PDF report ...")
        pdf_path = _default_pdf_path(image_path, reports_dir)
        ReportAgent().generate(final_report, pdf_path)
        final_report["pdf_path"] = pdf_path
        print(f"      -> Saved: {pdf_path}")

    print("Pipeline complete.")
    return final_report


def main():
    parser = argparse.ArgumentParser(description="Run the Argus-AI disaster detection pipeline on an image.")
    parser.add_argument("--image", required=True, help="Path to the input image.")
    parser.add_argument("--city", required=True, help="City name for weather/news verification.")
    parser.add_argument("--fire-model", default="models/fire_detection/best.pt", help="Path to fire YOLO model.")
    parser.add_argument("--landslide-model", default="models/landslide_classification/best_model.pt", help="Path to landslide model.")
    parser.add_argument("--mode", default="both", choices=["fire", "landslide", "both"], help="Which detectors to run.")
    parser.add_argument("--output", default=None, help="Optional path to save the JSON report.")
    parser.add_argument("--reports-dir", default=DEFAULT_REPORTS_DIR, help="Folder to save auto-generated PDF reports (default: reports/).")
    parser.add_argument("--no-pdf", action="store_true", help="Skip PDF report generation.")
    args = parser.parse_args()

    report = run_pipeline(
        image_path=args.image,
        city=args.city,
        fire_model_path=args.fire_model,
        landslide_model_path=args.landslide_model,
        mode=args.mode,
        reports_dir=args.reports_dir,
        generate_pdf=not args.no_pdf
    )

    print("\n===== FINAL REPORT =====")
    print(json.dumps(report, indent=2, default=str))

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, default=str)
        print(f"\nSaved JSON report to {args.output}")


if __name__ == "__main__":
    main()