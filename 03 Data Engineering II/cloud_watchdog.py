#!/usr/bin/env python

# Copyright 2017 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import json
import time

from google.cloud import pubsub_v1


def summarize(message):
    data = message.data.decode("utf-8")
    attributes = message.attributes

    event_type = attributes["eventType"]
    bucket_id = attributes["bucketId"]
    object_id = attributes["objectId"]
    generation = attributes["objectGeneration"]
    description = (
        "\tEvent type: {event_type}\n"
        "\tBucket ID: {bucket_id}\n"
        "\tObject ID: {object_id}\n"
        "\tGeneration: {generation}\n"
    ).format(
        event_type=event_type,
        bucket_id=bucket_id,
        object_id=object_id,
        generation=generation,
    )

    if "overwroteGeneration" in attributes:
        description += f"\tOverwrote generation: {attributes['overwroteGeneration']}\n"
    if "overwrittenByGeneration" in attributes:
        description += f"\tOverwritten by generation: {attributes['overwrittenByGeneration']}\n"

    payload_format = attributes["payloadFormat"]
    if payload_format == "JSON_API_V1":
        object_metadata = json.loads(data)
        size = object_metadata["size"]
        content_type = object_metadata["contentType"]
        metageneration = object_metadata["metageneration"]
        description += (
            "\tContent type: {content_type}\n"
            "\tSize: {object_size}\n"
            "\tMetageneration: {metageneration}\n"
        ).format(
            content_type=content_type,
            object_size=size,
            metageneration=metageneration,
        )
    return description


def poll_notifications(project, subscription_name):
    """Polls a Cloud Pub/Sub subscription for new GCS events for display."""
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(
        project, subscription_name
    )

    def callback(message):
        print(f"Received message:\n{summarize(message)}")
        message.ack()

    subscriber.subscribe(subscription_path, callback=callback)

    # The subscriber is non-blocking, so we must keep the main thread from
    # exiting to allow it to process messages in the background.
    print(f"Listening for messages on {subscription_path}")
    while True:
        time.sleep(60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "project", help="The ID of the project that owns the subscription"
    )
    parser.add_argument(
        "subscription", help="The ID of the Pub/Sub subscription"
    )
    args = parser.parse_args()
    poll_notifications(args.project, args.subscription)
