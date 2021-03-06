#!/usr/bin/env python

# Copyright 2019 Google, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from six.moves.urllib.request import urlopen
import os
import uuid

import beta_snippets
from google.cloud import storage
import pytest
from flaky import flaky


POSSIBLE_TEXTS = [
    "Google",
    "SUR",
    "SUR",
    "ROTO",
    "Vice President",
    "58oo9",
    "LONDRES",
    "OMAR",
    "PARIS",
    "METRO",
    "RUE",
    "CARLO",
]


@pytest.fixture(scope="session")
def video_path(tmpdir_factory):
    file = urlopen("http://storage.googleapis.com/cloud-samples-data/video/cat.mp4")
    path = tmpdir_factory.mktemp("video").join("file.mp4")
    with open(str(path), "wb") as f:
        f.write(file.read())

    return str(path)


@pytest.fixture(scope="function")
def bucket():
    # Create a temporaty bucket to store annotation output.
    bucket_name = str(uuid.uuid1())
    storage_client = storage.Client()
    bucket = storage_client.create_bucket(bucket_name)

    yield bucket

    # Teardown.
    bucket.delete(force=True)


@pytest.mark.slow
def test_speech_transcription(capsys):
    beta_snippets.speech_transcription(
        "gs://python-docs-samples-tests/video/googlework_short.mp4"
    )
    out, _ = capsys.readouterr()
    assert "cultural" in out


@pytest.mark.slow
def test_detect_labels_streaming(capsys, video_path):
    beta_snippets.detect_labels_streaming(video_path)

    out, _ = capsys.readouterr()
    assert "cat" in out


@pytest.mark.slow
def test_detect_shot_change_streaming(capsys, video_path):
    beta_snippets.detect_shot_change_streaming(video_path)

    out, _ = capsys.readouterr()
    assert "Shot" in out


@pytest.mark.slow
def test_track_objects_streaming(capsys, video_path):
    beta_snippets.track_objects_streaming(video_path)

    out, _ = capsys.readouterr()
    assert "cat" in out


@pytest.mark.slow
def test_detect_explicit_content_streaming(capsys, video_path):
    beta_snippets.detect_explicit_content_streaming(video_path)

    out, _ = capsys.readouterr()
    assert "Time" in out


@pytest.mark.slow
def test_annotation_to_storage_streaming(capsys, video_path, bucket):
    output_uri = "gs://{}".format(bucket.name)
    beta_snippets.annotation_to_storage_streaming(video_path, output_uri)

    out, _ = capsys.readouterr()
    assert "Storage" in out


# Flaky timeout
@flaky(max_runs=3, min_passes=1)
def test_detect_text(capsys):
    in_file = "./resources/googlework_tiny.mp4"
    beta_snippets.video_detect_text(in_file)
    out, _ = capsys.readouterr()
    assert 'Text' in out


# Flaky timeout
@flaky(max_runs=3, min_passes=1)
def test_detect_text_gcs(capsys):
    in_file = "gs://python-docs-samples-tests/video/googlework_tiny.mp4"
    beta_snippets.video_detect_text_gcs(in_file)
    out, _ = capsys.readouterr()
    assert 'Text' in out


@pytest.mark.slow
def test_track_objects(capsys):
    in_file = "./resources/googlework_tiny.mp4"
    beta_snippets.track_objects(in_file)
    out, _ = capsys.readouterr()
    assert "Entity id" in out


@pytest.mark.slow
def test_track_objects_gcs():
    in_file = "gs://cloud-samples-data/video/cat.mp4"
    object_annotations = beta_snippets.track_objects_gcs(in_file)

    text_exists = False
    for object_annotation in object_annotations:
        if "CAT" in object_annotation.entity.description.upper():
            text_exists = True
    assert text_exists
    assert object_annotations[0].frames[0].normalized_bounding_box.left >= 0.0
    assert object_annotations[0].frames[0].normalized_bounding_box.left <= 1.0


# Flaky Gateway
@flaky(max_runs=3, min_passes=1)
def test_streaming_automl_classification(capsys, video_path):
    project_id = os.environ["GCLOUD_PROJECT"]
    model_id = "VCN6363999689846554624"
    beta_snippets.streaming_automl_classification(video_path, project_id, model_id)
    out, _ = capsys.readouterr()
    assert "brush_hair" in out
