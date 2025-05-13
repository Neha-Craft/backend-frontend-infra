#!/usr/bin/env python3
import os

import aws_cdk as cdk

from iac_infra.iac_infra_stack import IacInfraStack


app = cdk.App()
IacInfraStack(app, "PrimumAiAuthService",
    # Using specific Account and Region
    env=cdk.Environment(account='148761648660', region='eu-west-1'),
)

app.synth()