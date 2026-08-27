# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
import typing
import json


@gl.evm.contract_interface
class _Recipient:
    class View:
        pass

    class Write:
        pass


class ClinicalTrialMilestoneEscrow(gl.Contract):
    deployer: str
    trial_count: u256
    milestone_count: u256
    report_count: u256
    trials: TreeMap[u256, str]
    trial_status: TreeMap[u256, str]
    trial_phases: TreeMap[u256, str]
    trial_budgets: TreeMap[u256, u256]
    trial_sponsor: TreeMap[u256, str]
    trial_lab: TreeMap[u256, str]
    trial_delegate: TreeMap[u256, str]
    milestone_trial: TreeMap[u256, u256]
    milestone_names: TreeMap[u256, str]
    milestone_amounts: TreeMap[u256, u256]
    milestone_status: TreeMap[u256, str]
    milestone_paid: TreeMap[u256, u256]
    milestone_recipient: TreeMap[u256, str]
    escrow_received: TreeMap[u256, u256]
    report_milestone: TreeMap[u256, u256]
    report_uri: TreeMap[u256, str]
    report_digest: TreeMap[u256, str]
    report_status: TreeMap[u256, str]
    report_reason: TreeMap[u256, str]
    report_submitter: TreeMap[u256, str]
    used_digests: TreeMap[str, str]

    def __init__(self):
        self.deployer = str(gl.message.sender_address)
        self.trial_count = u256(0)
        self.milestone_count = u256(0)
        self.report_count = u256(0)

    @gl.public.write
    def create_trial(self, trial_key: str, phase: str, budget: u256, lab: str) -> typing.Any:
        if len(trial_key) == 0 or len(trial_key) > 64:
            return "INVALID_TRIAL_KEY"
        if phase not in ("PHASE_I", "PHASE_II", "PHASE_III"):
            return "INVALID_PHASE"
        if len(lab) == 0:
            return "INVALID_LAB"
        try:
            normalized_lab = str(Address(lab))
        except Exception:
            return "INVALID_LAB"
        if trial_key in self.trials:
            return "TRIAL_EXISTS"
        trial_id = self.trial_count
        self.trials[trial_id] = trial_key
        self.trial_status[trial_id] = "ACTIVE"
        self.trial_phases[trial_id] = phase
        self.trial_budgets[trial_id] = budget
        self.trial_sponsor[trial_id] = str(gl.message.sender_address)
        self.trial_lab[trial_id] = normalized_lab
        self.trial_delegate[trial_id] = ""
        self.trial_count = trial_id + u256(1)
        return trial_id

    @gl.public.write
    def set_trial_delegate(self, trial_id: u256, delegate: str) -> typing.Any:
        if trial_id >= self.trial_count:
            return "TRIAL_NOT_FOUND"
        if self.trial_sponsor[trial_id] != str(gl.message.sender_address):
            return "SPONSOR_ONLY"
        if len(delegate) == 0:
            return "INVALID_DELEGATE"
        try:
            self.trial_delegate[trial_id] = str(Address(delegate))
        except Exception:
            return "INVALID_DELEGATE"
        return "DELEGATE_SET"

    @gl.public.write
    def add_milestone(self, trial_id: u256, name: str, amount: u256, recipient: str) -> typing.Any:
        if trial_id >= self.trial_count:
            return "TRIAL_NOT_FOUND"
        if self.trial_sponsor[trial_id] != str(gl.message.sender_address):
            return "SPONSOR_ONLY"
        if len(name) == 0 or len(name) > 128:
            return "INVALID_MILESTONE"
        if len(recipient) == 0:
            return "INVALID_RECIPIENT"
        if amount == u256(0):
            return "INVALID_AMOUNT"
        if self.trial_budgets[trial_id] < amount:
            return "EXCEEDS_TRIAL_BUDGET"
        milestone_id = self.milestone_count
        self.milestone_trial[milestone_id] = trial_id
        self.milestone_names[milestone_id] = name
        self.milestone_amounts[milestone_id] = amount
        self.milestone_status[milestone_id] = "PENDING"
        self.milestone_paid[milestone_id] = u256(0)
        self.milestone_recipient[milestone_id] = recipient
        self.escrow_received[milestone_id] = u256(0)
        self.trial_budgets[trial_id] = self.trial_budgets[trial_id] - amount
        self.milestone_count = milestone_id + u256(1)
        return milestone_id

    @gl.public.write.payable
    def fund_milestone(self, milestone_id: u256) -> typing.Any:
        if milestone_id >= self.milestone_count:
            return "MILESTONE_NOT_FOUND"
        trial_id = self.milestone_trial[milestone_id]
        if self.trial_sponsor[trial_id] != str(gl.message.sender_address):
            return "SPONSOR_ONLY"
        if self.milestone_status[milestone_id] != "PENDING":
            return "MILESTONE_NOT_FUNDABLE"
        amount = gl.message.value
        expected = self.milestone_amounts[milestone_id]
        if amount == u256(0):
            return "ZERO_VALUE"
        if amount != expected:
            return "WRONG_ESCROW_VALUE"
        self.escrow_received[milestone_id] = amount
        self.milestone_status[milestone_id] = "FUNDED"
        return "FUNDED"

    @gl.public.write
    def submit_report(self, milestone_id: u256, report_uri: str, digest: str) -> typing.Any:
        if milestone_id >= self.milestone_count:
            return "MILESTONE_NOT_FOUND"
        trial_id = self.milestone_trial[milestone_id]
        sender = str(gl.message.sender_address)
        if sender != self.trial_lab[trial_id] and sender != self.trial_delegate[trial_id]:
            return "LAB_OR_DELEGATE_ONLY"
        if self.milestone_status[milestone_id] != "FUNDED":
            return "MILESTONE_NOT_PENDING"
        if len(report_uri) == 0 or len(report_uri) > 512 or not report_uri.startswith("ipfs://"):
            return "INVALID_REPORT_URI"
        if len(digest) == 0 or len(digest) > 128 or digest in self.used_digests:
            return "DIGEST_REUSED"
        report_id = self.report_count
        self.report_milestone[report_id] = milestone_id
        self.report_uri[report_id] = report_uri
        self.report_digest[report_id] = digest
        self.report_status[report_id] = "PENDING"
        self.report_reason[report_id] = ""
        self.report_submitter[report_id] = str(gl.message.sender_address)
        self.used_digests[digest] = "USED"
        self.report_count = report_id + u256(1)
        self.milestone_status[milestone_id] = "REPORT_SUBMITTED"
        return report_id

    @gl.public.write
    def validate_report(self, report_id: u256) -> typing.Any:
        if report_id >= self.report_count:
            return "REPORT_NOT_FOUND"
        if self.report_status[report_id] != "PENDING":
            return "REPORT_ALREADY_VALIDATED"
        uri = self.report_uri[report_id]
        digest = self.report_digest[report_id]

        # Studio's web adapter rejects the ipfs:// scheme. Keep the immutable
        # ipfs URI in storage, but resolve it through a HTTPS gateway for fetch.
        fetch_uri = uri
        if uri.startswith("ipfs://"):
            fetch_uri = "https://ipfs.io/ipfs/" + uri[7:]

        def run() -> str:
            response = gl.nondet.web.get(fetch_uri)
            content = response.body.decode("utf-8")
            prompt = ("Validate this anonymized clinical-trial milestone report. "
                      "Check inclusion/exclusion compliance, sample size, adverse "
                      "events, and FDA/EMA safety threshold. Return ONLY JSON with "
                      "compliant (true/false), risk (LOW/MEDIUM/HIGH/CRITICAL), "
                      "reason (string), digest (string). Report: " + content[:4000] +
                      " Expected digest: " + digest)
            return gl.nondet.exec_prompt(prompt)

        raw = gl.eq_principle.prompt_comparative(run, principle="clinical protocol compliance")
        try:
            cleaned = raw
            if isinstance(cleaned, str):
                cleaned = cleaned.strip()
                if cleaned.startswith("```"):
                    lines = cleaned.split("\n")
                    if len(lines) >= 3 and lines[0].startswith("```") and lines[-1].strip() == "```":
                        cleaned = "\n".join(lines[1:-1]).strip()
                        if cleaned.startswith("json"):
                            cleaned = cleaned[4:].lstrip()
            data = cleaned if not isinstance(cleaned, str) else json.loads(cleaned)
            compliant = data["compliant"]
            risk = data["risk"]
            reason = data["reason"]
        except Exception:
            return "INVALID_AI_RESULT"
        if not isinstance(compliant, bool) or not isinstance(risk, str) or not isinstance(reason, str):
            return "INVALID_AI_RESULT"
        if risk not in ("LOW", "MEDIUM", "HIGH", "CRITICAL") or len(reason) > 1024:
            return "INVALID_AI_RESULT"
        if compliant == True and risk in ("LOW", "MEDIUM"):
            self.report_status[report_id] = "APPROVED"
            self.report_reason[report_id] = reason
            self.milestone_status[self.report_milestone[report_id]] = "APPROVED"
            return "APPROVED"
        self.report_status[report_id] = "REJECTED"
        self.report_reason[report_id] = reason
        self.milestone_status[self.report_milestone[report_id]] = "REJECTED"
        return "REJECTED"

    @gl.public.write
    def release_milestone(self, milestone_id: u256) -> typing.Any:
        if milestone_id >= self.milestone_count:
            return "MILESTONE_NOT_FOUND"
        if self.milestone_status[milestone_id] != "APPROVED":
            return "NOT_APPROVED"
        amount = self.milestone_amounts[milestone_id]
        if self.milestone_paid[milestone_id] != u256(0):
            return "ALREADY_RELEASED"
        if self.escrow_received[milestone_id] != amount:
            return "INSUFFICIENT_ESCROW"
        self.milestone_paid[milestone_id] = amount
        self.milestone_status[milestone_id] = "RELEASED"
        _Recipient(Address(self.milestone_recipient[milestone_id])).emit_transfer(value=amount)
        return "RELEASED"

    @gl.public.write
    def refund_milestone(self, milestone_id: u256) -> typing.Any:
        if milestone_id >= self.milestone_count:
            return "MILESTONE_NOT_FOUND"
        status = self.milestone_status[milestone_id]
        if status != "REJECTED":
            return "NOT_REFUNDABLE"
        amount = self.escrow_received[milestone_id]
        if amount == u256(0) or self.milestone_paid[milestone_id] != u256(0):
            return "NOTHING_TO_REFUND"
        trial_id = self.milestone_trial[milestone_id]
        self.escrow_received[milestone_id] = u256(0)
        self.milestone_paid[milestone_id] = amount
        self.trial_budgets[trial_id] = self.trial_budgets[trial_id] + amount
        self.milestone_status[milestone_id] = "REFUNDED"
        _Recipient(Address(self.trial_sponsor[trial_id])).emit_transfer(value=amount)
        return "REFUNDED"

    @gl.public.view
    def read_milestone(self, milestone_id: u256) -> typing.Any:
        if milestone_id >= self.milestone_count:
            return "MILESTONE_NOT_FOUND"
        return self.milestone_status[milestone_id]
