import os
from sec_edgar_downloader import Downloader

def download_filings(tickers, num_filings, save_dir):
    """
    Downloads 10-K and 10-Q filings for a given list of tickers.
    """
    # Initialize the downloader with user-agent details.
    dl = Downloader("dd-copilot", "admin@ddcopilot.local", save_dir)
    
    for ticker in tickers:
        print(f"Downloading {num_filings} 10-K and 10-Q filings for {ticker}...")
        try:
            dl.get("10-K", ticker, limit=num_filings)
            dl.get("10-Q", ticker, limit=num_filings)
        except Exception as e:
            print(f"Failed to download for {ticker}: {e}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    save_dir = os.path.join(base_dir, "data", "raw")
    tickers = ["AAPL", "MSFT", "TSLA", "JPM", "PFE"]
    
    print(f"Saving filings to: {save_dir}")
    download_filings(tickers, 3, save_dir)
    print("Download complete.")
