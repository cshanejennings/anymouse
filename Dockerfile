FROM public.ecr.aws/lambda/python:3.9

# Copy requirements first for better layer caching
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install dependencies
RUN pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Download spaCy model if not already included
RUN python -m spacy download en_core_web_sm || echo "Model already available"

# Copy application code
COPY anymouse/ ${LAMBDA_TASK_ROOT}/anymouse/

# Set the CMD to your handler
CMD ["anymouse.lambda_handler.lambda_handler"]