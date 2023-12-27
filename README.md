# FolderSyncer

FolderSyncer is a Python-based tool for synchronizing the contents of two folders: a source and a replica. It ensures that the replica is an identical copy of the source folder, performing one-way synchronization.

## Features

- **One-Way Synchronization**: Ensures the replica folder's contents exactly match the source folder.
- **Periodic Synchronization**: Performs synchronization at user-defined intervals.
- **Logging**: Records file operations to a log file and console output.
- **Command Line Arguments**: Users can specify folder paths, synchronization intervals, and the log file path via command line arguments.
- **Robust Error Handling**: Capable of handling various file system errors.

## Installation

Clone the repository:

```bash
git clone https://github.com/jejejekeie/Veeam_TestTask.git
cd Veeam_TestTask

python FolderSyncer.py <source_folder> <replica_folder> <sync_interval_in_seconds> <log_file_path> [options]
