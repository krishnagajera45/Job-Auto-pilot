# Operational Runbooks

## Automation Failure
1. Check application-automation logs for failed job ID.
2. Retry the automation job in the queue.
3. If repeated failure, switch to manual assist workflow.

## Auth Outage
1. Verify auth-service health endpoint.
2. Rotate secrets if JWT validation fails.
3. Fail over to backup auth instance.

## Vector Store Latency
1. Check Qdrant status and disk usage.
2. Reduce query concurrency and batch retrieval.
3. Rebuild indexes if performance regresses.
