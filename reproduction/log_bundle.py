#!/usr/bin/env python3
from pathlib import Path
import json, trackio
ROOT=Path(__file__).resolve().parents[1]
trackio.init(project="llm-judge-scaling-repro",name="cpu-three-claim-reproduction",
 config={"openreview_id":"ANVg7NnupP","claims":3,"device":"cpu","model_calls":0},
 embed=False,auto_log_gpu=False,auto_log_cpu=False)
a=trackio.Artifact("llm-judge-scaling-cpu-reproduction",type="dataset",
 description="Exact softmax-ratio quadrature, Monte Carlo cross-checks, best-of-k certificates, tests, and provenance.")
a.add_dir(ROOT/"reproduction",name="reproduction"); a.add_dir(ROOT/"outputs",name="outputs")
for n in ("paper.pdf","claims.md","SOURCE_AUDIT.md","ENVIRONMENT.md","README.md"): a.add_file(ROOT/n,name=n)
logged=trackio.log_artifact(a,aliases=["challenge","cpu","complete"]); trackio.finish()
print(json.dumps({"artifact":logged.qualified_name,"files":len(logged.manifest or []),"size":logged.size},sort_keys=True))

