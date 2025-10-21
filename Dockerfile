# Start from a default ubuntu image.
FROM python:latest

# Install GDB for advanced debugging.
RUN apt-get update && apt-get install -y \
  build-essential \
  gdb \
  && rm -rf /var/lib/apt/lists/*

# Install pip packages
RUN pip install python-magic

WORKDIR /

COPY . /

# Copy/Compile my fuzzer
COPY main.py /
RUN chmod +x /main.py
# Add python-magic installation line
RUN pip install python-magic

# Run it.
CMD ["python3", "main.py"]
