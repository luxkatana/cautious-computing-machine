
apply:
	./apply_to_production.sh

build:
	cd counter
	npm run build
	sudo mv build/* /var/www/chinesespypigeon.lol/dcounter

