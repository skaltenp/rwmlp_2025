# Usage 
This application demonstrates how to poll for GCS notifications from a
Cloud Pub/Sub subscription, parse the incoming message, and acknowledge the
successful processing of the message.

This application will work with any subscription configured for pull rather
than push notifications. If you do not already have notifications configured,
you may consult the docs [here](https://cloud.google.com/storage/docs/reporting-changes)

or 

follow the steps below:

0. Before starting, setup google cloud cli:
       https://cloud.google.com/sdk/docs/install?hl=de
   Then install google-cloud-storage library:
       https://cloud.google.com/storage/docs/reference/libraries
   Then install pubsub library:
       https://cloud.google.com/pubsub/docs/reference/libraries


1. First, follow the common setup steps for these snippets, specically
   configuring auth and installing dependencies. See the README's "Setup"
   section.

2. Activate the Google Cloud Pub/Sub API, if you have not already done so.
   https://console.cloud.google.com/flows/enableapi?apiid=pubsub

3. Create a Google Cloud Storage bucket:
   $ gsutil mb gs://testbucket_rwmlp_2025

4. Create a Cloud Pub/Sub topic and publish bucket notifications there:

   - $ gsutil notification create -f json -t update_topic gs://testbucket_rwmlp_2025

   - ($ gsutil notification create -f json -t greenspark_service_providers gs://dagashrae)

5. Create a subscription for your new topic:

   - $ gcloud pubsub subscriptions create update_topic_subscription --topic=update_topic

   - ($ gcloud pubsub subscriptions create greenspark_service_providers_data_updates_subscription --topic=greenspark_service_providers)

6. Run this program:

   - $ python cloud_watchdog.py dagrwmlp-420511 update_topic_subscription

   - ($ python cloud_watchdog.py dagrwmlp-420511 greenspark_service_providers_data_updates_subscription)

7. While the program is running, upload and delete some files in the testbucket
   bucket (you could use the console or gsutil) and watch as changes scroll by
   in the app.