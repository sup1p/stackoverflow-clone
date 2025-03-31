# StackOverflow Clone

Stack Overflow Clone — platform for sharing questions and answers in IT and techno sphere, with tag, voting, search and user profile with reputation and full editing support.

## Website link

👉 [Go to website](https://sof-frontend-fsxb.vercel.app/)  

### Main page
![Main](Screenshots/{4B148A81-E3C0-4EBD-9D36-FBF9BEF0A2B8}.png)

### Question page
![Question](Screenshots/{927F9168-8408-4FBE-9E7D-048646E1CC2A}.png)

### Tags
![Tags](Screenshots/{A441005D-35B4-43D3-A62D-2514C155C007}.png)



## Tech stack

### Backend:
- Python
- Django Rest Framework
- PostgreSQL

### Frontend:
- Next.js
- Axios

### Extra:
- Docker (optional)
- Gunicorn (on deploy)

## Deploy

- **Frontend**: [Vercel](https://vercel.com/)  
- **Backend**: [AWS EC2]
- **Database**: PostgreSQL on Supabase

## Local run

**Backend**  
```bash
cd backend
pip install -r requirements.txt
python manage.py runserver
