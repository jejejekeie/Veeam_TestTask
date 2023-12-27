import argparse
import logging
import os
import shutil
import sys
import time
import hashlib


class FolderSyncer:
    def __init__(self, source, replica, interval, logger):
        self.source = source
        self.replica = replica
        self.interval = interval
        self.logger = logger

    def run(self):
        try:
            while True:
                self.sync_directories()
                time.sleep(self.interval)
        except KeyboardInterrupt:
            self.logger.info("FolderSyncer interrupted by user.")
        except PermissionError as e:
            self.logger.error(f"Permission error encountered: {e}")
            # Handle permission errors
        except FileNotFoundError as e:
            self.logger.error(f"File not found error: {e}")
            # Handle file not found
        except OSError as e:
            self.logger.error(f"OS error encountered: {e}")
            # Handle other OS-level errors
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            # Handle other  exceptions

    def is_modified(self, source_item, replica_item):
        """Check if the source item was modified after the replica item was."""
        try:
            if not os.path.exists(replica_item):
                return True  # Replica doesn't exist, so considered modified

            source_mtime = os.path.getmtime(source_item)
            replica_mtime = os.path.getmtime(replica_item) if os.path.exists(replica_item) else 0

            if not os.path.getsize(source_item) != os.path.getsize(replica_item):
                return True

            return source_mtime > replica_mtime

        except OSError as e:
            self.logger.error(f"Error accessing file: {e}")
            return False

    def md5sum(self, fname):
        """Compute the MD5 sum of a file"""
        try:
            hash_md5 = hashlib.md5()
            with open(fname, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except OSError as e:
            self.logger.error(f"Error reading file for MD5: {e}")
            return None

    def update_items(self, current_s_dir, current_r_dir):
        for item in os.listdir(current_s_dir):
            s_item = os.path.join(current_s_dir, item)
            r_item = os.path.join(current_r_dir, item)
            try:
                if os.path.isdir(s_item):
                    if not os.path.exists(r_item):
                        os.makedirs(r_item)
                        self.logger.info(f"Directory created: {r_item}")

                    self.update_items(s_item, r_item)

                elif os.path.isfile(s_item):
                    if self.is_modified(s_item, r_item):
                        if not os.path.exists(r_item) or self.md5sum(s_item) != self.md5sum(r_item):
                            shutil.copy(s_item, r_item)
                            self.logger.info(f"File {'copied' if not os.path.exists(r_item) else 'updated'}: {r_item}")
            except FileNotFoundError as e:
                self.logger.error(f"Directory not found: {e}")
            except PermissionError as e:
                self.logger.error(f"Permission denied: {e}")

    def remove_deleted_items(self, current_s_dir, current_r_dir):
        try:
            for item in os.listdir(current_r_dir):
                r_item = os.path.join(current_r_dir, item)
                s_item = os.path.join(current_s_dir, item)

                if os.path.isdir(r_item):
                    if not os.path.exists(s_item):
                        shutil.rmtree(r_item)
                        self.logger.info(f"Directory deleted: {r_item}")
                    else:
                        self.remove_deleted_items(s_item, r_item)  # Recursive call for subdirectories
                elif os.path.isfile(r_item) and not os.path.exists(s_item):
                    if not os.path.exists(s_item):
                        os.remove(r_item)
                        self.logger.info(f"File deleted: {r_item}")

        except FileNotFoundError as e:
            self.logger.error(f"Directory not found in replica: {e}")
        except PermissionError as e:
            self.logger.error(f"Permission denied while accessing replica directory: {e}")
        except OSError as e:
            self.logger.error(f"OS error occurred: {e}")

    def sync_directories(self):
        if not os.path.isdir(self.source):
            self.logger.error(f"Source is not a directory: {self.source}")
        if not os.path.exists(self.replica):
            os.makedirs(self.replica)
            self.logger.info(f'Replica directory created: {self.replica}')

        self.update_items(self.source, self.replica)
        self.remove_deleted_items(self.source, self.replica)


def configure_logging(log_file, verbose):
    logger = logging.getLogger('FolderSyncer')
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger


def cleanup_log(log_file, logger=None):
    """Erase log file content"""
    try:
        with open(log_file, 'w'):
            pass
        if logger:
            logger.info(f"Log file {log_file} content cleared successfully.")
    except OSError as e:
        if logger:
            logger.error(f"Error clearing log file content: {e}")
        else:
            print(f"Error clearing log file content: {e}")
            sys.exit(1)


def parse_args():
    parser = argparse.ArgumentParser(
        prog='FolderSyncer',
        description='Sync a folder'
    )
    parser.add_argument('source', help='Source folder path')
    parser.add_argument('replica', help='Replica folder path')
    parser.add_argument('interval', type=int, help='Synchronization interval in seconds')
    parser.add_argument('log_file', help='Path for the log file')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging')
    parser.add_argument('-c', '--cleanup-log', action='store_true', help='Clean up log file before starting')
    return parser.parse_args()


def main():
    args = parse_args()
    logger = configure_logging(args.log_file, args.verbose)

    if args.cleanup_log:
        cleanup_log(args.log_file, logger)

    syncer = FolderSyncer(args.source, args.replica, args.interval, logger)
    syncer.run()


if __name__ == "__main__":
    main()
