FROM debian:12

# Install SSH server and required packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    openssh-server \
    unzip \
    ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Create SSH directory
RUN mkdir -p /var/run/sshd

# Create fictional analyst account
RUN useradd -m -s /bin/bash analyst && \
    echo 'analyst:NightShift104' | chpasswd

# Copy challenge files
COPY challenge_files/.note /home/analyst/.note
COPY challenge_files/app.log /var/log/app.log
COPY challenge_files/final_report.zip /home/analyst/final_report.zip
COPY challenge_files/archive_sync /etc/cron.d/archive_sync

# Set file ownership
RUN chown -R analyst:analyst /home/analyst

# Configure startup script
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Expose SSH
EXPOSE 22

# Start SSH service
CMD ["/start.sh"]