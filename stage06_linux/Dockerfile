FROM debian:12-slim

# Install the SSH server
RUN apt-get update && apt-get install -y openssh-server unzip && rm -rf /var/lib/apt/lists/*
RUN mkdir -p /var/run/sshd

# Create the fictional analyst account with the EC-05 password
RUN useradd -m -s /bin/bash analyst && echo 'analyst:NightShift104' | chpasswd

# Put the challenge files into the analyst's home
COPY challenge_files/.note       /home/analyst/.note
COPY challenge_files/app.log     /var/log/app.log
COPY challenge_files/final_report.zip /home/analyst/final_report.zip
RUN chown -R analyst:analyst /home/analyst

COPY start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 22
CMD ["/start.sh"]
