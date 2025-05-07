#!/usr/bin/env python3
import os

import aws_cdk as cdk

from iac_infra.iac_infra_stack import BackendInfraStack

app = cdk.App()
BackendInfraStack(app, "PrimumAiStageStack",
    env=cdk.Environment(account='148761648660', region='ap-south-1')
)

app.synth()
