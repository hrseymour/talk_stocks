sudo lsof -i :443
sudo lsof -i :443 | awk 'NR>1 {print $2}' | xargs -r sudo kill
