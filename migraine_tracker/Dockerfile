ARG BUILD_FROM
FROM $BUILD_FROM

# Set the working directory
WORKDIR /usr/src/app

# Install Python and other dependencies
RUN apk add --no-cache python3 py3-pip

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the port
EXPOSE 8000

# Set the command to run the application
CMD [ "python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000" ]
