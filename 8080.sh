rm -f *.log

# hypercorn --config hypercorn_config.py server.py:app &
nohup hypercorn --config hypercorn_config.py server.py:app &> output.log &

