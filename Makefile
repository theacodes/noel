.PHONY: all
all:
	$(MAKE) -C noel all
	$(MAKE) -C kubectl all
	$(MAKE) -C remote-builder all
	$(MAKE) -C http-frontend all

.PHONY: teardown
teardown:
	-kubectl delete -f remote-builder/spec.yaml
	-kubectl delete -f http-frontend/spec.yaml
	-kubectl delete -f noel/spec.yaml
