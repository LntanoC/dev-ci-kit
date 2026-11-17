import pathlib
import unittest

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / '.github' / 'workflows'
ASSETS = ROOT / 'skills' / 'dev-ci' / 'assets'


def load(path):
    with path.open(encoding='utf-8') as stream:
        return yaml.load(stream, Loader=yaml.BaseLoader)


class WorkflowTests(unittest.TestCase):
    def test_reusable_workflows_have_valid_calls(self):
        for path in (WORKFLOWS / name for name in ('java.yml', 'frontend.yml', 'security.yml', 'ocr-review.yml', 'security-audit.yml')):
            with self.subTest(path=path.name):
                workflow = load(path)
                self.assertIn('workflow_call', workflow['on'])
                self.assertTrue(workflow['jobs'])

    def test_example_inputs_and_secrets_match_workflows(self):
        for path in ASSETS.glob('*.yml'):
            workflow = load(path)
            for job in workflow['jobs'].values():
                reference = job['uses']
                prefix = 'LntanoC/dev-ci-kit/.github/workflows/'
                self.assertTrue(reference.startswith(prefix), reference)
                target = reference[len(prefix):].split('@', 1)[0]
                definition = load(WORKFLOWS / target)['on']['workflow_call'] or {}
                self.assertLessEqual(set(job.get('with', {})), set(definition.get('inputs', {})))
                declared = definition.get('secrets', {})
                self.assertLessEqual(set(job.get('secrets', {})), set(declared))
                required = {name for name, spec in declared.items() if spec.get('required') == 'true'}
                self.assertLessEqual(required, set(job.get('secrets', {})))

    def test_ocr_is_limited_to_trusted_same_repo_pull_requests(self):
        job = load(WORKFLOWS / 'ocr-review.yml')['jobs']['review']
        condition = job['if']
        for clause in ('pull_request', 'head.repo.full_name == github.repository', 'OWNER', 'MEMBER', 'COLLABORATOR', '!github.event.pull_request.draft'):
            self.assertIn(clause, condition)
        self.assertEqual(job['permissions']['contents'], 'read')
        self.assertEqual(job['permissions']['pull-requests'], 'write')

    def test_no_workflow_uses_pull_request_target(self):
        for path in list(WORKFLOWS.glob('*.yml')) + list(ASSETS.glob('*.yml')):
            with self.subTest(path=path):
                triggers = load(path)['on']
                self.assertNotIn('pull_request_target', triggers)

    def test_audit_is_manual_private_and_read_only(self):
        workflow = load(WORKFLOWS / 'security-audit.yml')
        job = workflow['jobs']['audit']
        self.assertIn("github.event_name == 'workflow_dispatch'", job['if'])
        self.assertIn('github.event.repository.private', job['if'])
        self.assertIn('github.event.repository.default_branch', job['if'])
        self.assertEqual(job['permissions'], {'contents': 'read'})
        step = next(s for s in job['steps'] if s.get('id') == 'audit')
        self.assertIn('--permission-mode read-only --approval-policy never', step['run'])
        self.assertIn('Do not execute target code', step['run'])
        self.assertEqual(step['env']['DEEPSEEK_API_KEY'], '${{ secrets.deepseek-api-key }}')
        install = next(s for s in job['steps'] if s.get('name') == 'Install DeepSeek Harness')
        self.assertIn('@deepseek-ai/dsh@latest', install['run'])
        self.assertIn('npm list', install['run'])
        guidance = next(s for s in job['steps'] if s.get('name') == 'Check out audit guidance')
        self.assertEqual(guidance['with']['repository'], 'cloudflare/security-audit-skill')
        self.assertNotIn('ref', guidance['with'])
        version = next(s for s in job['steps'] if s.get('name') == 'Record audit guidance version')
        self.assertEqual(version['run'], 'git -C audit-guidance rev-parse HEAD')


if __name__ == '__main__':
    unittest.main()
