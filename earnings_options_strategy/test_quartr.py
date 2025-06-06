from clients.quartr_client import QuartrClient
from datetime import datetime, timedelta
import json

def print_json(data):
    """Helper function to print JSON data in a readable format."""
    print(json.dumps(data, indent=2))

def main():
    client = QuartrClient()
    
    # Test earnings call transcript
    print("\nTesting earnings call transcript for ORCL:")
    transcript = client.get_earnings_call_transcript("ORCL")
    if transcript:
        print("\nTranscript metadata:")
        print(f"Call date: {transcript.get('call_date')}")
        print(f"Duration: {transcript.get('duration')}")
        print(f"Number of participants: {len(transcript.get('participants', []))}")
        print("\nFirst 500 characters of transcript:")
        print(transcript.get('transcript', '')[:500] + "...")
    
    # Test management tone analysis
    print("\nTesting management tone analysis for ORCL:")
    tone_data = client.get_management_tone("ORCL")
    if tone_data:
        print("\nTone analysis results:")
        print(f"Overall sentiment: {tone_data.get('overall_sentiment')}")
        print(f"CEO sentiment: {tone_data.get('ceo_sentiment')}")
        print(f"CFO sentiment: {tone_data.get('cfo_sentiment')}")
        print("\nKey topics discussed:")
        for topic in tone_data.get('key_topics', []):
            print(f"- {topic}")
    
    # Test earnings call highlights
    print("\nTesting earnings call highlights for ORCL:")
    highlights = client.get_earnings_call_highlights("ORCL")
    if highlights:
        print("\nCall highlights:")
        print("\nKey points:")
        for point in highlights.get('key_points', []):
            print(f"- {point}")
        print("\nGuidance:")
        print(highlights.get('guidance', 'No guidance provided'))
        print("\nRisks:")
        for risk in highlights.get('risks', []):
            print(f"- {risk}")
        print("\nOpportunities:")
        for opp in highlights.get('opportunities', []):
            print(f"- {opp}")
    
    # Test analyst Q&A summary
    print("\nTesting analyst Q&A summary for ORCL:")
    qa_summary = client.get_analyst_qa_summary("ORCL")
    if qa_summary:
        print("\nQ&A Summary:")
        print(f"Analyst sentiment: {qa_summary.get('analyst_sentiment')}")
        print("\nKey questions and answers:")
        for q, a in zip(qa_summary.get('questions', []), qa_summary.get('answers', [])):
            print(f"Q: {q}")
            print(f"A: {a}\n")
        print("\nKey concerns raised:")
        for concern in qa_summary.get('key_concerns', []):
            print(f"- {concern}")
    
    # Test comprehensive metrics
    print("\nTesting comprehensive earnings call metrics for ORCL:")
    metrics = client.get_earnings_call_metrics("ORCL")
    if metrics:
        print("\nComprehensive metrics:")
        print(f"Management tone: {metrics.get('management_tone')}")
        print(f"Analyst sentiment: {metrics.get('analyst_sentiment')}")
        print(f"Guidance confidence: {metrics.get('guidance_confidence')}")
        print(f"Risk level: {metrics.get('risk_level')}")
        print("\nKey metrics discussed:")
        for metric in metrics.get('key_metrics', []):
            print(f"- {metric}")
        print("\nKey concerns:")
        for concern in metrics.get('key_concerns', []):
            print(f"- {concern}")

if __name__ == "__main__":
    main() 