# 1. Start with an official lightweight Python runtime environment
FROM python:3.13-slim

# 2. Set the working directory inside the container system
WORKDIR /app

# 3. Copy only the requirements list file first to leverage cache optimization
COPY requirements.txt .

# 4. Install all the application dependencies cleanly without caching installation files
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the application source code files into the container
COPY . .

# 6. Expose the port number that FastAPI will run on
EXPOSE 8000

# 7. Run the command to launch the Uvicorn production server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]