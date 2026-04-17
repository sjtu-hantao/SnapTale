# Use the official Python image from the Docker Hub
FROM registry.cn-hangzhou.aliyuncs.com/base_mj/vmbook:latest

# Set the working directory in the container
WORKDIR /backend

# Copy the requirements file into the container
COPY ./requirements.txt /backend/requirements.txt

# Install the required dependencies
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# Copy the rest of the application code into the container
COPY ./ /backend/


# Expose the port that the app runs on
EXPOSE 8000


# Command to run the application
WORKDIR /backend/app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]