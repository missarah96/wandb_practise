import os
import wandb
import wandb.apis.reports as wr
import json  # Add this import for json.dumps()

assert os.getenv('WANDB_API_KEY'), 'You must set the WANDB_API_KEY environment variable'

def get_baseline_run(entity='hamelsmu', project='my-report-project', tag='baseline'):
    api = wandb.Api()
    runs = api.runs(f'{entity}/{project}', {"tags": {"$in": [tag]}})
    assert len(runs) == 1, 'There must be exactly one run with the tag "baseline"'
    return runs[0]

def compare_runs(entity='hamelsmu',
                 project='cicd_demo',
                 tag='baseline',
                 run_id=None):
    entity = os.getenv('WANDB_ENTITY') or entity
    project = os.getenv('WANDB_PROJECT') or project
    tag = os.getenv('BASELINE_TAG') or tag
    run_id = os.getenv('RUN_ID') or run_id
    assert run_id, 'You must set the RUN_ID environment variable or pass a `run_id` argument'

    baseline = get_baseline_run(entity=entity, project=project, tag=tag)

    # Create the report
    report = wr.Report(entity=entity, project=project,
                       title='Compare Runs',
                       description=f"A comparison of runs, the baseline run name is {baseline.name}") 

    # Convert filters dictionary to a valid JSON string
    filters = json.dumps({'ID': {'$in': [run_id, baseline.id]}})
    
    # Use the stringified filter for the Runset constructor
    runset = wr.Runset(entity, project, "Run Comparison", filters=filters)

    # Create a panel with the run comparison
    pg = wr.PanelGrid(
        runsets=[runset],
        panels=[wr.RunComparer(diff_only='split', layout={'w': 24, 'h': 15})]
    )

    # Add the panel to the report
    report.blocks = report.blocks[:1] + [pg] + report.blocks[1:]
    report.save()

    if os.getenv('CI'):  # is set to `true` in GitHub Actions
        with open(os.environ['GITHUB_OUTPUT'], 'a') as f:  # write the output variable REPORT_URL to the GITHUB_OUTPUT file
            print(f'REPORT_URL={report.url}', file=f)
    
    return report.url

if __name__ == '__main__':
    print(f'The comparison report can be found at: {compare_runs()}')
