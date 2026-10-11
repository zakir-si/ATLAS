# Colab workflow

1. Open atlas_baseline.ipynb in Google Colab and select a GPU runtime if available.
2. Review model/dataset terms and verify the dataset text field.
3. Start with a small permitted model, dataset and step count.
4. Run the baseline first and save the manifest/logs.
5. Compare a candidate using the same split, token budget and evaluation protocol.
6. Download artifacts to your own storage; Colab sessions are temporary.

The notebook implements a LoRA baseline. It is not a novel algorithm and does not prove ATLAS is more efficient.


## Repository-integrated measurement notebook

Open [`atlas_colab_measurements.ipynb`](atlas_colab_measurements.ipynb) in Google Colab. It clones the current `main` branch of this repository, imports ATLAS's `RunResult` and benchmark helper, runs a small LoRA baseline, and exports a JSON manifest including the checked-out ATLAS commit SHA. It does not claim the baseline is an ATLAS optimization or infer task quality from validation loss. The current benchmark API needs a normalized task-specific quality score before a valid comparison can be made.
