# Learning Cloud - Django Backend

A comprehensive Django-based learning management system designed for kids in grades 1-4, with support for students, teachers, and parents. Built to handle 20+ million students with optimized performance and scalability.

## 🚀 Features

### Core Functionality
- **Multi-role Authentication**: Students (ID + PIN), Teachers, Parents, and Admins
- **Grade-based Content**: Organized content for grades 1-4
- **Interactive Learning**: Lessons, quizzes, activities with multimedia support
- **Progress Tracking**: Comprehensive progress monitoring and analytics
- **Multilingual Support**: English, Amharic, Arabic, French, Spanish
- **Offline Access**: Download content for offline learning
- **Gamification**: Achievements, streaks, and rewards system

### Technical Features
- **Scalable Architecture**: Optimized for 20M+ students
- **High Performance**: Redis caching, database indexing, CDN integration
- **Security**: Encrypted PINs, rate limiting, secure authentication
- **Analytics**: Comprehensive reporting and insights
- **Notifications**: Multi-channel notification system
- **API-First**: RESTful APIs with OAuth2 authentication

## 🏗️ Architecture

### Database Design
- **PostgreSQL**: Primary database with optimized indexing
- **Prisma**: Database schema management and migrations
- **Redis**: Caching and session management
- **AWS S3**: Media file storage and CDN

### Application Structure
```
learning_cloud/
├── apps/
│   ├── accounts/          # User management and authentication
│   ├── content/           # Content management (lessons, subjects)
│   ├── quizzes/           # Quiz system and assessments
│   ├── progress/          # Progress tracking and analytics
│   ├── analytics/         # System analytics and reporting
│   └── notifications/     # Notification system
├── learning_cloud/        # Django project settings
├── prisma/               # Database schema
└── requirements.txt      # Python dependencies
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.9+
- PostgreSQL 13+
- Redis 6+
- Node.js 16+ (for Prisma)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Learning_cloud_api_v1
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
npm install prisma @prisma/client
```

### 4. Environment Configuration
```bash
cp env.example .env
# Edit .env with your configuration
```

### 5. Database Setup
```bash
# Start PostgreSQL and Redis services
# Create database
createdb learning_cloud

# Run Prisma migrations
npx prisma migrate dev

# Generate Prisma client
npx prisma generate
```

### 6. Django Setup
```bash
# Run Django migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Create logs directory
mkdir logs
```

### 7. Start Development Server
```bash
# Start Redis (in separate terminal)
redis-server

# Start Celery worker (in separate terminal)
celery -A learning_cloud worker -l info

# Start Django development server
python manage.py runserver
```

## 📊 Database Schema

### Key Models

#### Users & Authentication
- **User**: Custom user model with role-based access
- **School**: School management
- **UserSession**: Session tracking
- **LoginAttempt**: Security monitoring

#### Content Management
- **Subject**: Grade-level subjects
- **Chapter**: Subject chapters
- **Lesson**: Individual lessons with multimedia
- **LessonMedia**: Media file management
- **ContentAccess**: Access control

#### Learning & Assessment
- **Quiz**: Assessment quizzes
- **Question**: Quiz questions with multiple types
- **QuizAttempt**: Student quiz attempts
- **Answer**: Student answers

#### Progress Tracking
- **StudentProgress**: Lesson progress tracking
- **LearningStreak**: Learning streak management
- **SubjectProgress**: Subject-level progress
- **GradeProgress**: Grade-level progress
- **ProgressMilestone**: Achievement tracking

#### Analytics & Reporting
- **Analytics**: System-wide analytics
- **UserEngagement**: User engagement metrics
- **ContentAnalytics**: Content performance
- **SchoolAnalytics**: School-level analytics
- **SystemAnalytics**: System-wide metrics

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/student-login/` - Student login with ID + PIN
- `POST /api/auth/teacher-login/` - Teacher login
- `POST /api/auth/parent-login/` - Parent login
- `POST /api/auth/logout/` - Logout

### Content Management
- `GET /api/subjects/` - List subjects by grade
- `GET /api/chapters/` - List chapters
- `GET /api/lessons/` - List lessons
- `GET /api/lessons/{id}/` - Get lesson details
- `GET /api/search/` - Search content

### Quizzes & Assessments
- `GET /api/quizzes/` - List quizzes
- `POST /api/quizzes/attempts/start/` - Start quiz attempt
- `POST /api/quizzes/sessions/{session_key}/submit-answer/` - Submit answer
- `POST /api/quizzes/sessions/{session_key}/complete/` - Complete quiz

### Progress Tracking
- `GET /api/progress/` - Get student progress
- `POST /api/progress/lessons/{id}/update/` - Update lesson progress
- `GET /api/progress/stats/` - Get progress statistics
- `GET /api/progress/streak/` - Get learning streak

### Analytics & Reporting
- `GET /api/analytics/` - Get analytics data
- `GET /api/analytics/reports/` - Get reports

## 🔒 Security Features

### Authentication & Authorization
- OAuth2 token-based authentication
- Role-based access control (RBAC)
- Encrypted PIN storage for students
- Session management with Redis

### Data Protection
- Rate limiting on API endpoints
- CORS configuration
- SQL injection prevention
- XSS protection
- CSRF protection

### Monitoring & Logging
- Login attempt tracking
- Security event logging
- Performance monitoring
- Error tracking

## 📈 Performance Optimization

### Database Optimization
- Strategic indexing for 20M+ records
- Connection pooling
- Query optimization
- Database partitioning (future)

### Caching Strategy
- Redis for session storage
- Query result caching
- Static file caching
- CDN integration

### Scalability Features
- Horizontal scaling support
- Load balancing ready
- Microservices architecture
- Container deployment ready

## 🌍 Internationalization

### Supported Languages
- English (default)
- Amharic
- Arabic
- French
- Spanish

### Implementation
- Django i18n framework
- Language-specific content
- RTL support for Arabic
- Localized date/time formats

## 📱 Mobile & Offline Support

### Offline Features
- Content download capability
- Offline progress tracking
- Sync when online
- Progressive Web App (PWA) ready

### Mobile Optimization
- Responsive API design
- Mobile-specific endpoints
- Push notification support
- Touch-friendly interfaces

## 🚀 Deployment

### Production Deployment
```bash
# Install production dependencies
pip install gunicorn

# Set production environment variables
export DJANGO_SETTINGS_MODULE=learning_cloud.settings
export DEBUG=False

# Run database migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Start production server
gunicorn learning_cloud.wsgi:application
```

### Docker Deployment
```dockerfile
# Dockerfile example
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "learning_cloud.wsgi:application"]
```

### Environment Variables
See `env.example` for all required environment variables.

## 📊 Monitoring & Analytics

### Built-in Analytics
- User engagement tracking
- Content performance metrics
- Learning progress analytics
- System performance monitoring

### Reporting Features
- Daily/Weekly/Monthly reports
- Custom report generation
- Export capabilities
- Real-time dashboards

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Code Standards
- Follow PEP 8 for Python code
- Use type hints where appropriate
- Write comprehensive tests
- Document all APIs

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Documentation
- API documentation: `/api/docs/`
- Database schema: `prisma/schema.prisma`
- Configuration: `env.example`

### Getting Help
- Check the documentation
- Review the code comments
- Open an issue for bugs
- Contact the development team

## 🔮 Future Enhancements

### Planned Features
- AI-powered personalized learning
- Advanced gamification
- Parent-teacher communication
- Advanced analytics dashboard
- Mobile app development
- Voice recognition for assessments
- Augmented reality content

### Technical Improvements
- Microservices architecture
- GraphQL API
- Real-time features with WebSockets
- Advanced caching strategies
- Machine learning integration
- Blockchain for certificates

---

**Learning Cloud** - Empowering education through technology for the next generation of learners.
