# bash -c "python client.py 0" & 
# bash -c "python client.py 1" & 
# bash -c "python client.py 2" &
bash -c "python player.py 0" & 
bash -c "python player.py 1" & 
bash -c "python player.py 2" &
bash -c "python coordinator.py"