import os
import re
import requests
from urllib.parse import urlparse
import zipfile
from io import BytesIO
import argparse
import sys
import time
from tqdm import tqdm
import socket
import shutil

def parse_github_folder_url(url):
    """Parse a GitHub URL to extract owner, repo, branch, and folder path."""
    # Clean URL (remove trailing slashes)
    url = url.rstrip("/")
    
    # Check if the URL is a valid GitHub URL
    if not re.match(r"https?://github\.com/[\w-]+/[\w.-]+", url):
        raise ValueError("Invalid GitHub URL")
    
    # Extract path components from URL
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.strip("/").split("/")
    
    if len(path_parts) < 2:
        raise ValueError("URL does not point to a GitHub repository")
    
    owner = path_parts[0]
    repo = path_parts[1]
    
    # Default branch is 'main' if not specified
    branch = 'main'
    folder_path = ''
    
    # Check if the URL contains 'tree' or 'blob' to determine branch and folder path
    if len(path_parts) > 2 and path_parts[2] in ['tree', 'blob']:
        branch = path_parts[3] if len(path_parts) > 3 else branch
        folder_path = '/'.join(path_parts[4:]) if len(path_parts) > 4 else ''
    
    return owner, repo, branch, folder_path

def download_with_progress(url, timeout=30, retries=3, backoff_factor=1.5):
    """Download file with progress bar and retry logic."""
    current_retry = 0
    
    while current_retry <= retries:
        try:
            # Stream the response to show progress
            response = requests.get(url, stream=True, timeout=timeout)
            response.raise_for_status()  # Raise exception for non-200 status codes
            
            # Get file size if available
            total_size = int(response.headers.get('content-length', 0))
            
            # Initialize progress bar
            progress_bar = tqdm(
                total=total_size, 
                unit='B', 
                unit_scale=True, 
                desc="Downloading"
            )
            
            content = BytesIO()
            
            # Download with progress updates
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    content.write(chunk)
                    progress_bar.update(len(chunk))
            
            progress_bar.close()
            content.seek(0)
            return content
        
        except (requests.exceptions.RequestException, socket.timeout) as e:
            current_retry += 1
            if current_retry <= retries:
                wait_time = backoff_factor ** current_retry
                print(f"\nConnection error: {str(e)}")
                print(f"Retrying in {wait_time:.1f} seconds... (Attempt {current_retry}/{retries})")
                time.sleep(wait_time)
            else:
                print(f"\nFailed after {retries} attempts: {str(e)}")
                raise

def sanitize_path(path):
    """Sanitize a file path to ensure it's valid on the current OS."""
    # Replace characters that are problematic in file paths
    # Remove trailing slashes that can cause issues on Windows
    return path.rstrip('/\\')

def extract_to_temp_and_move(zip_ref, target_files, folder_prefix, output_dir):
    """Extract files to a temp directory first, then move them to avoid permission issues."""
    temp_dir = os.path.join(os.path.dirname(output_dir), f"temp_extract_{int(time.time())}")
    
    try:
        os.makedirs(temp_dir, exist_ok=True)
        
        # Extract files with progress
        print(f"Found {len(target_files)} files to extract")
        
        for file in tqdm(target_files, desc="Extracting"):
            try:
                # Get relative path by removing the repo and folder prefix
                rel_path = file[len(folder_prefix):]
                if not rel_path:
                    continue
                
                # Sanitize the path
                rel_path = sanitize_path(rel_path)
                
                # Create the directory structure in temp dir
                target_file_path = os.path.join(temp_dir, rel_path)
                os.makedirs(os.path.dirname(target_file_path), exist_ok=True)
                
                # Extract the file
                with zip_ref.open(file) as source, open(target_file_path, "wb") as target:
                    target.write(source.read())
            except Exception as e:
                print(f"\nWarning: Failed to extract {file}: {e}")
                continue
        
        # Now move from temp dir to output dir
        print(f"Moving files to final destination...")
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Get all items in temp dir
        items = os.listdir(temp_dir)
        
        for item in tqdm(items, desc="Moving files"):
            src_path = os.path.join(temp_dir, item)
            dst_path = os.path.join(output_dir, item)
            
            # Remove destination if it exists
            if os.path.exists(dst_path):
                if os.path.isdir(dst_path):
                    shutil.rmtree(dst_path, ignore_errors=True)
                else:
                    os.unlink(dst_path)
            
            # Move the item
            try:
                shutil.move(src_path, dst_path)
            except Exception as e:
                print(f"\nWarning: Failed to move {item}: {e}")
    
    finally:
        # Clean up temp dir
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except:
                print(f"Note: Could not remove temporary directory: {temp_dir}")

def download_github_folder(url, output_dir=None):
    """Download a specific folder from a GitHub repository."""
    try:
        # Parse GitHub URL
        owner, repo, branch, folder_path = parse_github_folder_url(url)
        
        # If no output directory specified, use the folder name
        if output_dir is None:
            output_dir = os.path.basename(folder_path) if folder_path else repo
        
        # Sanitize output directory name
        output_dir = sanitize_path(output_dir)
        
        print(f"Target: {folder_path if folder_path else 'root'} from {owner}/{repo} (branch: {branch})")
        
        # Construct archive URL - use codeload.github.com directly
        archive_url = f"https://codeload.github.com/{owner}/{repo}/zip/refs/heads/{branch}"
        
        # Download the zip file with progress
        print(f"Source: {archive_url}")
        try:
            zip_content = download_with_progress(archive_url)
        except Exception as e:
            # Try alternative URL format as fallback
            print(f"Trying alternative download URL...")
            archive_url = f"https://github.com/{owner}/{repo}/archive/{branch}.zip"
            zip_content = download_with_progress(archive_url)
        
        print("\nPreparing extraction...")
        # Extract only the folder we want from the zip
        with zipfile.ZipFile(zip_content) as zip_ref:
            repo_dir_prefix = f"{repo}-{branch}/"
            folder_prefix = repo_dir_prefix + folder_path + "/" if folder_path else repo_dir_prefix
            
            # Get list of files in the target folder
            target_files = [
                file for file in zip_ref.namelist()
                if file.startswith(folder_prefix) and file != folder_prefix
            ]
            
            if not target_files:
                raise Exception(f"Folder '{folder_path}' not found in repository")
            
            # Extract files using the safer method
            extract_to_temp_and_move(zip_ref, target_files, folder_prefix, output_dir)
            
        print(f"\n✅ Successfully downloaded folder to: {os.path.abspath(output_dir)}")
        return True
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False

def main():
    # Set up command-line argument parser
    parser = argparse.ArgumentParser(
        description="Download a specific folder from a GitHub repository"
    )
    parser.add_argument(
        "url", 
        help="GitHub URL of the folder to download (e.g., https://github.com/owner/repo/tree/branch/folder)"
    )
    parser.add_argument(
        "-o", "--output", 
        help="Output directory name (default: folder name)"
    )
    parser.add_argument(
        "-t", "--timeout", 
        type=int, 
        default=60,
        help="Connection timeout in seconds (default: 60)"
    )
    parser.add_argument(
        "-r", "--retries", 
        type=int, 
        default=3,
        help="Number of retries for failed downloads (default: 3)"
    )
    parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="Force overwrite if output directory exists"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    print("\n📦 GitHub Folder Downloader")
    print("-" * 40)
    
    # Check if output directory exists and --force not used
    if args.output and os.path.exists(args.output) and not args.force:
        print(f"Output directory '{args.output}' already exists.")
        response = input("Do you want to overwrite? (y/N): ").strip().lower()
        if response != 'y':
            print("Download cancelled.")
            sys.exit(0)
    
    # Download the folder
    try:
        result = download_github_folder(args.url, args.output)
        
        # Return appropriate exit code
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\nDownload cancelled by user")
        sys.exit(1)

if __name__ == "__main__":
    main()