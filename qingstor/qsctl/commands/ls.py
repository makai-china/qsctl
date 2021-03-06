# =========================================================================
# Copyright (C) 2016 Yunify, Inc.
# -------------------------------------------------------------------------
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this work except in compliance with the License.
# You may obtain a copy of the License in the LICENSE file, or at:
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =========================================================================

import time

from qingstor.sdk.config import Config
from qingstor.sdk.service.qingstor import QingStor

from .base import BaseCommand

from ..utils import format_size, json_loads
from ..constants import HTTP_OK

# Format used to pretty print directories.
format_directory = " " * 30


class LsCommand(BaseCommand):

    command = "ls"
    usage = "%(prog)s <qs-path> [-c <conf_file> -r <recusively> -p <page_size>]"

    @classmethod
    def add_extra_arguments(cls, parser):
        parser.add_argument(
            "-z",
            "--zone",
            dest="zone",
            help="List buckets located in this zone")

        parser.add_argument(
            "qs_path", nargs="?", default="qs://", help="The qs-path to list")

        parser.add_argument(
            "-p",
            "--page-size",
            dest="page_size",
            type=int,
            default=20,
            help="The number of results to return in each response")

        parser.add_argument(
            "-r",
            "--recursive",
            action="store_true",
            dest="recursive",
            help="Recursively list keys")
        return parser

    @classmethod
    def list_buckets(cls, options):
        location = ""
        if options.zone:
            location = options.zone
        resp = cls.client.list_buckets(location=location)
        if resp.status_code == HTTP_OK:
            buckets = resp['buckets']
            for bucket in sorted(buckets, key=lambda x: x["name"]):
                print(bucket["name"])

    @classmethod
    def print_to_console(cls, keys, dirs):
        for d in sorted(dirs):
            print("Directory" + format_directory + d)
        for key in sorted(keys, key=lambda x: x["key"]):
            created_time = time.strftime(
                "%Y-%m-%d %X UTC",
                time.strptime(key["created"], "%Y-%m-%dT%H:%M:%S.000Z"))
            if key["mime_type"] == "application/x-directory":
                print(created_time + format_size(key["size"]).rjust(12) + " " *
                      4 + key["key"] + "  (application/x-directory)")
            else:
                print(created_time + format_size(key["size"]).rjust(12) + " " *
                      4 + key["key"])

    @classmethod
    def list_keys(cls, options):
        bucket, prefix = cls.validate_qs_path(options.qs_path)

        delimiter = ""
        limit = 200
        marker = ""

        if options.recursive is False:
            delimiter = "/"
        if options.page_size is not None:
            limit = options.page_size

        while True:
            keys, marker, dirs = cls.list_multiple_keys(
                bucket, marker=marker, delimiter=delimiter, limit=limit)
            cls.print_to_console(keys, dirs)
            if marker == "":
                break

    @classmethod
    def send_request(cls, options):
        if options.qs_path == "qs://":
            cls.list_buckets(options)
        else:
            cls.list_keys(options)
