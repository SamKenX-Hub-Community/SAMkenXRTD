import json
from contextlib import contextmanager
from pathlib import Path
from unittest import mock

import pytest
from django_dynamic_fixture import get

from readthedocs.builds.storage import BuildMediaFileSystemStorage
from readthedocs.projects.constants import GENERIC, MKDOCS, SPHINX
from readthedocs.projects.models import Feature, HTMLFile, Project

data_path = Path(__file__).parent.resolve() / 'data'


@pytest.mark.django_db
@pytest.mark.search
class TestParsers:

    def setup_method(self):
        self.feature = get(
            Feature,
            feature_id=Feature.INDEX_FROM_HTML_FILES,
        )
        self.project = get(
            Project,
            slug='test',
            main_language_project=None,
        )
        self.version = self.project.versions.first()

    def _mock_open(self, content):
        @contextmanager
        def f(*args, **kwargs):
            read_mock = mock.MagicMock()
            read_mock.read.return_value = content
            yield read_mock
        return f


    @mock.patch.object(BuildMediaFileSystemStorage, 'exists')
    @mock.patch.object(BuildMediaFileSystemStorage, 'open')
    def test_mkdocs_default_theme(self, storage_open, storage_exists):
        local_path = data_path / 'mkdocs/in/mkdocs-1.1/'
        storage_exists.return_value = True

        self.project.feature_set.add(self.feature)
        self.version.documentation_type = MKDOCS
        self.version.save()

        parsed_json = []

        all_files = [
            'index.html',
            '404.html',
            'configuration.html',
            'no-title.html',
            'no-main-header.html',
        ]
        for file_name in all_files:
            file = local_path / file_name
            storage_open.reset_mock()
            storage_open.side_effect = self._mock_open(file.open().read())
            file = get(
                HTMLFile,
                project=self.project,
                version=self.version,
                path=file_name,
            )
            parsed_json.append(file.processed_json)

        expected_json = json.load(open(data_path / 'mkdocs/out/mkdocs-1.1.json'))
        assert parsed_json == expected_json

    @mock.patch.object(BuildMediaFileSystemStorage, 'exists')
    @mock.patch.object(BuildMediaFileSystemStorage, 'open')
    def test_mkdocs_gitbook_theme(self, storage_open, storage_exists):
        file = data_path / 'mkdocs/in/gitbook/index.html'
        storage_exists.return_value = True

        self.project.feature_set.add(self.feature)
        self.version.documentation_type = MKDOCS
        self.version.save()

        storage_open.side_effect = self._mock_open(file.open().read())
        file = get(
            HTMLFile,
            project=self.project,
            version=self.version,
            path='index.html',
        )
        parsed_json = [file.processed_json]
        expected_json = json.load(open(data_path / 'mkdocs/out/gitbook.json'))
        assert parsed_json == expected_json

    @mock.patch.object(BuildMediaFileSystemStorage, 'exists')
    @mock.patch.object(BuildMediaFileSystemStorage, 'open')
    def test_mkdocs_material_theme(self, storage_open, storage_exists):
        file = data_path / 'mkdocs/in/material/index.html'
        storage_exists.return_value = True

        self.project.feature_set.add(self.feature)
        self.version.documentation_type = MKDOCS
        self.version.save()

        storage_open.side_effect = self._mock_open(file.open().read())
        file = get(
            HTMLFile,
            project=self.project,
            version=self.version,
            path='index.html',
        )
        parsed_json = [file.processed_json]
        expected_json = json.load(open(data_path / 'mkdocs/out/material.json'))
        assert parsed_json == expected_json

    @mock.patch.object(BuildMediaFileSystemStorage, 'exists')
    @mock.patch.object(BuildMediaFileSystemStorage, 'open')
    def test_mkdocs_windmill_theme(self, storage_open, storage_exists):
        file = data_path / 'mkdocs/in/windmill/index.html'
        storage_exists.return_value = True

        self.project.feature_set.add(self.feature)
        self.version.documentation_type = MKDOCS
        self.version.save()

        storage_open.side_effect = self._mock_open(file.open().read())
        file = get(
            HTMLFile,
            project=self.project,
            version=self.version,
            path='index.html',
        )
        parsed_json = [file.processed_json]
        expected_json = json.load(open(data_path / 'mkdocs/out/windmill.json'))
        assert parsed_json == expected_json

    @mock.patch.object(BuildMediaFileSystemStorage, 'exists')
    @mock.patch.object(BuildMediaFileSystemStorage, 'open')
    def test_mkdocs_readthedocs_theme(self, storage_open, storage_exists):
        self.project.feature_set.add(self.feature)
        storage_exists.return_value = True
        self.version.documentation_type = MKDOCS
        self.version.save()

        local_path = data_path / 'mkdocs/in/readthedocs-1.1/'
        parsed_json = []

        for file_name in ['index.html', '404.html', 'versions.html']:
            file = local_path / file_name
            storage_open.reset_mock()
            storage_open.side_effect = self._mock_open(file.open().read())
            file = get(
                HTMLFile,
                project=self.project,
                version=self.version,
                path=file_name,
            )
            parsed_json.append(file.processed_json)

        expected_json = json.load(open(data_path / 'mkdocs/out/readthedocs-1.1.json'))
        assert parsed_json == expected_json


    @mock.patch.object(BuildMediaFileSystemStorage, 'exists')
    @mock.patch.object(BuildMediaFileSystemStorage, 'open')
    def test_sphinx(self, storage_open, storage_exists):
        json_file = data_path / 'sphinx/in/page.json'
        html_content = data_path / 'sphinx/in/page.html'

        json_content = json.load(json_file.open())
        json_content['body'] = html_content.open().read()
        storage_open.side_effect = self._mock_open(
            json.dumps(json_content)
        )
        storage_exists.return_value = True

        self.version.documentation_type = SPHINX
        self.version.save()

        page_file = get(
            HTMLFile,
            project=self.project,
            version=self.version,
            path='page.html',
        )

        parsed_json = page_file.processed_json
        expected_json = json.load(open(data_path / 'sphinx/out/page.json'))
        assert parsed_json == expected_json

    @mock.patch.object(BuildMediaFileSystemStorage, 'exists')
    @mock.patch.object(BuildMediaFileSystemStorage, 'open')
    def test_sphinx_page_without_title(self, storage_open, storage_exists):
        json_file = data_path / 'sphinx/in/no-title.json'
        html_content = data_path / 'sphinx/in/no-title.html'

        json_content = json.load(json_file.open())
        json_content['body'] = html_content.open().read()
        storage_open.side_effect = self._mock_open(
            json.dumps(json_content)
        )
        storage_exists.return_value = True

        self.version.documentation_type = SPHINX
        self.version.save()

        page_file = get(
            HTMLFile,
            project=self.project,
            version=self.version,
            path='no-title.html',
        )

        parsed_json = page_file.processed_json
        expected_json = json.load(open(data_path / 'sphinx/out/no-title.json'))
        assert parsed_json == expected_json

    @mock.patch.object(BuildMediaFileSystemStorage, "exists")
    @mock.patch.object(BuildMediaFileSystemStorage, "open")
    def test_sphinx_httpdomain(self, storage_open, storage_exists):
        json_file = data_path / "sphinx/in/httpdomain.json"
        html_content = data_path / "sphinx/in/httpdomain.html"

        json_content = json.load(json_file.open())
        json_content["body"] = html_content.open().read()
        storage_open.side_effect = self._mock_open(json.dumps(json_content))
        storage_exists.return_value = True

        self.version.save()

        page_file = get(
            HTMLFile,
            project=self.project,
            version=self.version,
            path="httpdomain.html",
        )

        parsed_json = page_file.processed_json
        expected_json = json.load(open(data_path / "sphinx/out/httpdomain.json"))
        assert parsed_json == expected_json

    @mock.patch.object(BuildMediaFileSystemStorage, "exists")
    @mock.patch.object(BuildMediaFileSystemStorage, "open")
    def test_sphinx_autodoc(self, storage_open, storage_exists):
        # Source:
        # https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#directive-automodule
        json_file = data_path / "sphinx/in/autodoc.json"
        html_content = data_path / "sphinx/in/autodoc.html"

        json_content = json.load(json_file.open())
        json_content["body"] = html_content.open().read()
        storage_open.side_effect = self._mock_open(json.dumps(json_content))
        storage_exists.return_value = True

        self.version.save()

        page_file = get(
            HTMLFile,
            project=self.project,
            version=self.version,
            path="autodoc.html",
        )

        parsed_json = page_file.processed_json
        expected_json = json.load(open(data_path / "sphinx/out/autodoc.json"))
        assert parsed_json == expected_json

    @mock.patch.object(BuildMediaFileSystemStorage, "exists")
    @mock.patch.object(BuildMediaFileSystemStorage, "open")
    def test_sphinx_local_toc(self, storage_open, storage_exists):
        """
        Test that the local table of contents from the ``contents``
        directive is not included in the indexed content.
        """
        # Source:
        # https://docs.readthedocs.io/en/stable/security.html
        html_content = data_path / "sphinx/in/local-toc.html"
        storage_open.side_effect = self._mock_open(html_content.open().read())
        storage_exists.return_value = True

        self.project.feature_set.add(self.feature)
        self.version.documentation_type = SPHINX
        self.version.save()

        page_file = get(
            HTMLFile,
            project=self.project,
            version=self.version,
            path="local-toc.html",
        )

        parsed_json = page_file.processed_json
        expected_json = json.load(open(data_path / "sphinx/out/local-toc.json"))
        assert parsed_json == expected_json

    @mock.patch.object(BuildMediaFileSystemStorage, "exists")
    @mock.patch.object(BuildMediaFileSystemStorage, "open")
    def test_sphinx_toctree(self, storage_open, storage_exists):
        """
        Test that the table of contents from the ``toctree``
        directive is not included in the indexed content.
        """
        # Source:
        # https://docs.readthedocs.io/en/stable/api/index.html
        html_content = data_path / "sphinx/in/toctree.html"
        json_content = {"body": html_content.open().read()}
        storage_open.side_effect = self._mock_open(json.dumps(json_content))
        storage_exists.return_value = True

        self.version.documentation_type = SPHINX
        self.version.save()

        page_file = get(
            HTMLFile,
            project=self.project,
            version=self.version,
            path="toctree.html",
        )

        parsed_json = page_file.processed_json
        expected_json = json.load(open(data_path / "sphinx/out/toctree.json"))
        assert parsed_json == expected_json

    @mock.patch.object(BuildMediaFileSystemStorage, "exists")
    @mock.patch.object(BuildMediaFileSystemStorage, "open")
    def test_sphinx_requests(self, storage_open, storage_exists):
        # Source:
        # https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#directive-automodule
        html_content = data_path / "sphinx/in/requests.html"

        json_content = {"body": html_content.open().read()}
        storage_open.side_effect = self._mock_open(json.dumps(json_content))
        storage_exists.return_value = True

        self.version.save()

        page_file = get(
            HTMLFile,
            project=self.project,
            version=self.version,
            path="requests.html",
        )

        parsed_json = page_file.processed_json
        expected_json = json.load(open(data_path / "sphinx/out/requests.json"))
        assert parsed_json == expected_json

    @mock.patch.object(BuildMediaFileSystemStorage, "exists")
    @mock.patch.object(BuildMediaFileSystemStorage, "open")
    def test_generic_simple_page(self, storage_open, storage_exists):
        file = data_path / "generic/in/basic.html"
        storage_exists.return_value = True
        self.version.documentation_type = GENERIC
        self.version.save()

        storage_open.side_effect = self._mock_open(file.open().read())
        file = get(
            HTMLFile,
            project=self.project,
            version=self.version,
            path="basic.html",
        )
        parsed_json = [file.processed_json]
        expected_json = json.load(open(data_path / "generic/out/basic.json"))
        assert parsed_json == expected_json

    @mock.patch.object(BuildMediaFileSystemStorage, "exists")
    @mock.patch.object(BuildMediaFileSystemStorage, "open")
    def test_generic_pelican_default_theme(self, storage_open, storage_exists):
        file = data_path / "pelican/in/default/index.html"
        storage_exists.return_value = True
        self.version.documentation_type = GENERIC
        self.version.save()

        storage_open.side_effect = self._mock_open(file.open().read())
        file = get(
            HTMLFile,
            project=self.project,
            version=self.version,
            path="index.html",
        )
        parsed_json = [file.processed_json]
        expected_json = json.load(open(data_path / "pelican/out/default.json"))
        assert parsed_json == expected_json
