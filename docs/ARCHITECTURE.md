# Architecture Mapping

The reference code preserves the draft's ordering as **security semantics**, not as a mandatory number of process boundaries, device crossings, or sequential hardware operations.

```text
CandidateRelease
  attributes + payload
       |
       v
ReleasePolicy.allows()
       |
       v
SQLiteExtractionState.reserve()  -- atomic bounded-state transition
       |
       v
ReleaseAuthorityIssuer.issue()   -- candidate/destination/epoch/state bound
       |
       v
FinalitySink.verify()
       |
       v
state.commit()                    -- terminal consume in reference profile
       |
       v
return payload                    -- first governed software external effect
```

A production implementation may fuse, pipeline, cache, batch, shard, or colocate these logical steps so long as it preserves the invariants.

## Candidate Release

The code does **not** equate one token with one Candidate Release. A Candidate Release is a deployment-selected externally effective unit. It can represent a privileged response, stream segment, tensor export, activation set, diagnostic object, or other bounded release.

## Non-bearer Release Authority

`ReleaseAuthority` is authenticated over:

- unique authority ID;
- reservation ID;
- candidate digest;
- model ID;
- release class;
- destination;
- epoch;
- scope key;
- quantity.

Copying the authority to another payload, destination, model, scope, or epoch fails sink verification.

## Finality Sink

The Python `FinalitySink` is the first **governed software API boundary** where payload bytes are returned. It does not claim to dominate DMA, debugger, shared-memory, telemetry, peer-GPU, or privileged-host paths. Production assurance requires moving or subordinating those paths to a stronger sink.
