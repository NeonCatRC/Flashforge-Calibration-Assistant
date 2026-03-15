#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Модуль для передачи файлов между компьютером и принтером по SCP

import paramiko
import os
import logging
import shlex
from typing import List, Dict, Optional
from scp import SCPClient


class SCPFileTransfer:
    # Класс для передачи файлов по SCP

    def __init__(self, host: str = '', username: str = '', password: str = '', timeout: int = 10):
        self.host = host
        self.username = username
        self.password = password
        self.timeout = timeout
        self.ssh_client = None
        self.scp_client = None

    # Устанавливает соединение
    def connect(self) -> bool:
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(
                self.host,
                username=self.username,
                password=self.password,
                timeout=self.timeout
            )
            self.scp_client = SCPClient(self.ssh_client.get_transport())
            return True
        except Exception as e:
            logging.error(f"SCP connection error: {str(e)}")
            return False

    # Закрывает соединение
    def disconnect(self) -> None:
        if self.scp_client:
            self.scp_client.close()
            self.scp_client = None

        if self.ssh_client:
            self.ssh_client.close()
            self.ssh_client = None

    # Загружает файл с удаленного сервера
    def get_file(self, remote_path: str, local_path: str) -> bool:
        if not self.scp_client:
            if not self.connect():
                return False

        try:
            local_dir = os.path.dirname(local_path)
            if local_dir and not os.path.exists(local_dir):
                os.makedirs(local_dir, exist_ok=True)

            self.scp_client.get(remote_path, local_path)
            return True
        except Exception as e:
            logging.error(f"File download error: {str(e)}")
            return False

    # Загружает файл на удаленный сервер
    def put_file(self, local_path: str, remote_path: str) -> bool:
        if not self.scp_client:
            if not self.connect():
                return False

        try:
            self.scp_client.put(local_path, remote_path)
            return True
        except Exception as e:
            logging.error(f"File upload error: {str(e)}")
            return False

    # Загружает несколько файлов с удаленного сервера
    def get_multiple_files(self, file_pairs: List[Dict[str, str]]) -> Dict[str, bool]:
        results = {}

        for file_pair in file_pairs:
            remote_path = file_pair.get('remote_path')
            local_path = file_pair.get('local_path')

            if not remote_path or not local_path:
                continue

            results[remote_path] = self.get_file(remote_path, local_path)

        return results

    # Загружает директорию с удаленного сервера
    def get_directory(self, remote_dir: str, local_dir: str, recursive: bool = True) -> int:
        if not self.scp_client:
            if not self.connect():
                return 0

        if not os.path.exists(local_dir):
            os.makedirs(local_dir, exist_ok=True)

        try:
            safe_dir = shlex.quote(remote_dir)
            command = f"find {safe_dir} -type f" if recursive else f"find {safe_dir} -maxdepth 1 -type f"
            stdin, stdout, stderr = self.ssh_client.exec_command(command)

            remote_files = [line.strip() for line in stdout.readlines() if line.strip()]

            downloaded_count = 0
            for remote_path in remote_files:
                rel_path = os.path.relpath(remote_path, remote_dir)
                local_path = os.path.join(local_dir, rel_path)

                local_file_dir = os.path.dirname(local_path)
                if not os.path.exists(local_file_dir):
                    os.makedirs(local_file_dir, exist_ok=True)

                if self.get_file(remote_path, local_path):
                    downloaded_count += 1

            return downloaded_count

        except Exception as e:
            logging.error(f"Directory download error: {str(e)}")
            return 0

    # Ищет файлы по шаблону в удаленной директории и загружает их
    def find_and_get_files(self, remote_dir: str, pattern: str, local_dir: str) -> List[str]:
        if not self.ssh_client:
            if not self.connect():
                return []

        try:
            if not os.path.exists(local_dir):
                os.makedirs(local_dir, exist_ok=True)

            command = f"find {shlex.quote(remote_dir)} -name {shlex.quote(pattern)} -type f"
            stdin, stdout, stderr = self.ssh_client.exec_command(command)

            remote_files = [line.strip() for line in stdout.readlines() if line.strip()]

            downloaded_files = []
            for remote_path in remote_files:
                local_path = os.path.join(local_dir, os.path.basename(remote_path))
                if self.get_file(remote_path, local_path):
                    downloaded_files.append(local_path)

            return downloaded_files

        except Exception as e:
            logging.error(f"Find and get files error: {str(e)}")
            return []
