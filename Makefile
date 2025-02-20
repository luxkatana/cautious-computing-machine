
apply:
	./apply_to_production.sh

build:
	sudo rm -rf /var/www/chinesespypigeon.lol/dcounter
	sudo mkdir /var/www/chinesespypigeon.lol/dcounter

	cd counter;npm run build;

	sudo mv counter/build/* /var/www/chinesespypigeon.lol/dcounter
	sudo systemctl reload apache2

