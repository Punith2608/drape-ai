const API_BASE = '';

export async function getSarees() {
  const response = await fetch('/api/sarees');

  if (!response.ok) {
    throw new Error('Failed to load sarees');
  }

  return response.json();
}

export async function getSareeById(id: string) {
  const response = await fetch(`/api/sarees/${encodeURIComponent(id)}`);

  if (!response.ok) {
    throw new Error('Failed to load saree');
  }

  return response.json();
}

export async function submitTryOnJob(sareeId: string) {
  const response = await fetch('/api/try-on', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ sareeId }),
  });

  if (!response.ok) {
    throw new Error('Failed to start virtual try-on');
  }

  return response.json();
}

export async function checkJobStatus(jobId: string) {
  const response = await fetch(
    `/api/try-on/${encodeURIComponent(jobId)}`
  );

  if (!response.ok) {
    throw new Error('Failed to check try-on status');
  }

  return response.json();
}

export async function getGallery() {
  const response = await fetch('/api/gallery');

  if (!response.ok) {
    throw new Error('Failed to load gallery');
  }

  return response.json();
}

export async function toggleFavourite(jobId: string) {
  const response = await fetch(
    `/api/gallery/${encodeURIComponent(jobId)}/favourite`,
    {
      method: 'POST',
    }
  );

  if (!response.ok) {
    throw new Error('Failed to update favourite');
  }

  return response.json();
}