VERSION?=0.4
TILT_PORT=26783
.PHONY: integrate disintegrate up down tag untag

integrate:
	cp daemon/forms/person.fields.yaml ../people/config/integration_chore-speech.nandy.io_person.fields.yaml
	cp daemon/forms/area.fields.yaml ../chore/config/integration_chore-speech.nandy.io_area.fields.yaml
	cp daemon/forms/act.fields.yaml ../chore/config/integration_chore-speech.nandy.io_act.fields.yaml
	cp daemon/forms/todo.fields.yaml ../chore/config/integration_chore-speech.nandy.io_todo.fields.yaml
	cp daemon/forms/routine.fields.yaml ../chore/config/integration_chore-speech.nandy.io_routine.fields.yaml

disintegrate:
	rm ../people/config/integration_chore-speech.nandy.io_person.fields.yaml
	rm ../chore/config/integration_chore-speech.nandy.io_area.fields.yaml
	rm ../chore/config/integration_chore-speech.nandy.io_act.fields.yaml
	rm ../chore/config/integration_chore-speech.nandy.io_todo.fields.yaml
	rm ../chore/config/integration_chore-speech.nandy.io_routine.fields.yaml

up: integrate
	kubectx docker-desktop
	tilt --port $(TILT_PORT) up

down: disintegrate
	kubectx docker-desktop
	tilt down

tag:
	-git tag -a "v$(VERSION)" -m "Version $(VERSION)"
	git push origin --tags

untag:
	-git tag -d "v$(VERSION)"
	git push origin ":refs/tags/v$(VERSION)"