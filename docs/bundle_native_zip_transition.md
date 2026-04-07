# Native Zip Transition

## Before this patch series finished

Before this patch series finished:

- you manually unzipped bundles,
- you ran the bundled `.ps1` from the extracted folder,
- and PatchOps did not yet own the raw-zip operator path end to end.

## After this patch series finished

After this patch series finished:

- you no longer manually unzip bundles,
- PatchOps accepts the `.zip`,
- PatchOps extracts it,
- PatchOps calls the bundled `.ps1`,
- and PatchOps writes one canonical report.

## Intended default operator flow

1. receive one zip bundle  
2. do **not** manually extract it  
3. run one PatchOps command or one-liner against the zip  
4. let PatchOps extract and invoke the bundled launcher  
5. read the canonical report

## Raw-zip command examples

```powershell
py -m patchops.cli check-bundle C:\path\to\patch_bundle.zip
py -m patchops.cli inspect-bundle C:\path\to\patch_bundle.zip
py -m patchops.cli plan-bundle C:\path\to\patch_bundle.zip
py -m patchops.cli apply-bundle C:\path\to\patch_bundle.zip --wrapper-root C:\dev\patchops
```

## Clarification

This transition is about PatchOps consuming a patch bundle zip directly.

It does not mean every delivery zip used to transport a patch package from somewhere else is automatically runnable without extraction. The milestone means the PatchOps repo itself now owns the raw-zip bundle flow.