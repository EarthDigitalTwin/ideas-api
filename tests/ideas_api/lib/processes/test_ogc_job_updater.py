#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Copyright 2024, by the California Institute of Technology. ALL RIGHTS RESERVED.
#  United States Government Sponsorship acknowledged. Any commercial use must be
#  negotiated with the Office of Technology Transfer at the California Institute of
#  Technology.  This software is subject to U.S. export control laws and regulations
#  and has been classified as EAR99.  By accepting this software, the user agrees to
#  comply with all applicable U.S. export laws and regulations.  User has the
#  responsibility to obtain export licenses, or other export authority as may be
#  required before exporting such information to foreign countries or providing
#  access to foreign persons.
#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os
from time import sleep
from unittest import TestCase

from ideas_api.lib.external_io.es_abstract import ESAbstract
from ideas_api.lib.external_io.es_factory import ESFactory
from ideas_api.lib.external_io.pub_sub_abstract import PubSubAbstract
from ideas_api.lib.external_io.pub_sub_factory import PubSubFactory
from ideas_api.lib.processes.ogc_job_updater import OgcJobUpdater
from ideas_api.lib.processes.ogc_jobs import OgcJobs


class TestOgcJobUpdater(TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.job_id = '987688b0-5237-43d4-b2ac-c22560df395b-2023-06-13T17:01:02.321072'

    def test_01_start_job(self):
        """
        :return:
        """
        es_middleware: ESAbstract = ESFactory().get_instance('AWS',
                                                             base_url='https://search-ideas-api-dev-1-f62xltsguioft2hpjepkrhln3e.us-west-2.es.amazonaws.com',
                                                             port=443,
                                                             index='NA')
        pub_sub: PubSubAbstract = PubSubFactory().get_instance('SNS').set_channel('arn:aws:sns:us-west-2:125113240993:ideas-project-ideas_api_main_topic')

        job_updater = OgcJobUpdater(es_middleware, pub_sub)
        first_job_trigger = {
            "messageType": "RESULT",
            "jobID": self.job_id,
            "status": "SUCCESSFUL",
            "stage": "PRE_PROCESSED",
        }
        job_updater.process_update(first_job_trigger)
        sleep(3)
        job_raw = OgcJobs(es_middleware).get_job_raw(self.job_id)
        self.assertEqual(34, job_raw['progress'], 'progress')
        self.assertTrue(job_raw['started'] > 0, 'finished')
        self.assertEqual('RUNNING', job_raw['status'], 'status')
        self.assertEqual('RRR:: starting', job_raw['message'], 'message')
        return

    def test_02_update_job(self):
        """
        :return:
        """
        es_middleware: ESAbstract = ESFactory().get_instance('AWS',
                                                             base_url='https://search-ideas-api-dev-1-f62xltsguioft2hpjepkrhln3e.us-west-2.es.amazonaws.com',
                                                             port=443,
                                                             index='NA')
        pub_sub: PubSubAbstract = PubSubFactory().get_instance('SNS').set_channel('arn:aws:sns:us-west-2:125113240993:ideas-project-ideas_api_main_topic')

        job_updater = OgcJobUpdater(es_middleware, pub_sub)
        first_job_trigger = {
            "messageType": "UPDATE",
            "jobID": self.job_id,
            "status": "RUNNING",
            "stage": "RRR",
            "message": "received job. starting it"
        }
        job_updater.process_update(first_job_trigger)
        sleep(3)
        job_raw = OgcJobs(es_middleware).get_job_raw(self.job_id)
        # self.assertEqual(34.32, job_raw['progress'], 'progress')
        # self.assertEqual('RUNNING', job_raw['status'], 'status')
        # self.assertEqual('RRR:: received job. starting it', job_raw['message'], 'message')
        result = OgcJobs(es_middleware).get_cached_result(job_raw)
        return

    def test_03_update_job(self):
        """
        :return:
        """
        es_middleware: ESAbstract = ESFactory().get_instance('AWS',
                                                             base_url='https://search-ideas-api-dev-1-f62xltsguioft2hpjepkrhln3e.us-west-2.es.amazonaws.com',
                                                             port=443,
                                                             index='NA')
        pub_sub: PubSubAbstract = PubSubFactory().get_instance('SNS').set_channel('arn:aws:sns:us-west-2:125113240993:ideas-project-ideas_api_main_topic')

        job_updater = OgcJobUpdater(es_middleware, pub_sub)
        first_job_trigger = {
            "messageType": "UPDATE",
            "jobID": self.job_id,
            "status": "RUNNING",
            "stage": "RRR",
            "message": "progressing. no error so far"
        }
        job_updater.process_update(first_job_trigger)
        sleep(3)
        job_raw = OgcJobs(es_middleware).get_job_raw(self.job_id)
        self.assertEqual(34.64, job_raw['progress'], 'progress')
        self.assertEqual('RUNNING', job_raw['status'], 'status')
        self.assertEqual('RRR:: progressing. no error so far', job_raw['message'], 'message')
        return

    def test_04_finish_job(self):
        """
        :return:
        """
        es_middleware: ESAbstract = ESFactory().get_instance('AWS',
                                                             base_url='https://search-ideas-api-dev-1-f62xltsguioft2hpjepkrhln3e.us-west-2.es.amazonaws.com',
                                                             port=443,
                                                             index='NA')
        pub_sub: PubSubAbstract = PubSubFactory().get_instance('SNS').set_channel('arn:aws:sns:us-west-2:125113240993:ideas-project-ideas_api_main_topic')

        job_updater = OgcJobUpdater(es_middleware, pub_sub)
        first_job_trigger = {
            "messageType": "RESULT",
            "jobID": self.job_id,
            "status": "SUCCESSFUL",
            "stage": "RRR",
            "message": "I have done it",
            "outputs": [
                {
                    "name": "DATA",
                    "value": "s3://foo/bar/data"
                },
                {
                    "name": "METADATA",
                    "value": "s3://foo/bar/METADATA"
                },
                {
                    "name": "ANCILLARY",
                    "value": "s3://foo/bar/ANCILLARY"
                }
            ],
        }
        job_updater.process_update(first_job_trigger)
        sleep(3)
        job_raw = OgcJobs(es_middleware).get_job_raw(self.job_id)
        self.assertEqual(67, job_raw['progress'], 'progress')
        self.assertEqual('RUNNING', job_raw['status'], 'status')
        self.assertEqual('RAPID:: starting', job_raw['message'], 'message')
        return

    def test_05_update_job(self):
        """
        :return:
        """
        es_middleware: ESAbstract = ESFactory().get_instance('AWS',
                                                             base_url='https://search-ideas-api-dev-1-f62xltsguioft2hpjepkrhln3e.us-west-2.es.amazonaws.com',
                                                             port=443,
                                                             index='NA')
        pub_sub: PubSubAbstract = PubSubFactory().get_instance('SNS').set_channel('arn:aws:sns:us-west-2:125113240993:ideas-project-ideas_api_main_topic')

        job_updater = OgcJobUpdater(es_middleware, pub_sub)
        first_job_trigger = {
            "messageType": "UPDATE",
            "jobID": self.job_id,
            "status": "RUNNING",
            "stage": "RAPID",
            "message": "progressing. some errors, but can be ignored"
        }
        job_updater.process_update(first_job_trigger)
        sleep(3)
        job_raw = OgcJobs(es_middleware).get_job_raw(self.job_id)
        self.assertEqual(67.32, job_raw['progress'], 'progress')
        self.assertEqual('RUNNING', job_raw['status'], 'status')
        self.assertEqual('RAPID:: progressing. some errors, but can be ignored', job_raw['message'], 'message')
        return

    def test_06_finish_job(self):
        """
        :return:
        """
        es_middleware: ESAbstract = ESFactory().get_instance('AWS',
                                                             base_url='https://search-ideas-api-dev-1-f62xltsguioft2hpjepkrhln3e.us-west-2.es.amazonaws.com',
                                                             port=443,
                                                             index='NA')
        pub_sub: PubSubAbstract = PubSubFactory().get_instance('SNS').set_channel('arn:aws:sns:us-west-2:125113240993:ideas-project-ideas_api_main_topic')

        job_updater = OgcJobUpdater(es_middleware, pub_sub)
        first_job_trigger = {
            "messageType": "RESULT",
            "jobID": self.job_id,
            "status": "SUCCESSFUL",
            "stage": "RAPID",
            "message": "it is done",
            "outputs": [
                {
                    "name": "DATA",
                    "value": "s3://foo/3DX2Y/data"
                },
                {
                    "name": "METADATA",
                    "value": "s3://foo/3DX2Y/METADATA"
                }
            ],
        }
        job_updater.process_update(first_job_trigger)
        sleep(3)
        job_raw = OgcJobs(es_middleware).get_job_raw(self.job_id)
        self.assertEqual(100, job_raw['progress'], 'progress')
        self.assertTrue(job_raw['finished'] > 0, 'finished')
        self.assertEqual('SUCCESSFUL', job_raw['status'], 'status')
        self.assertEqual(5, len(job_raw['job']['outputs']), 'outputs')
        self.assertEqual('RAPID:: it is done', job_raw['message'], 'message')
        return
