FROM gpikra/scalemamba:v1

WORKDIR /SCALE-MAMBA
COPY ./logistic_regressor.py /SCALE-MAMBA/logistic_regressor.py
COPY ./coordinator.py /SCALE-MAMBA/coordinator.py
COPY ./player.py /SCALE-MAMBA/player.py
COPY ./player_auxilliary.py /SCALE-MAMBA/player_auxilliary.py
COPY ./client.py /SCALE-MAMBA/client.py
COPY ./mock_researcher.py /SCALE-MAMBA/mock_researcher.py
COPY ./requirements.txt /SCALE-MAMBA/requirements.txt
RUN pip install -r requirements.txt