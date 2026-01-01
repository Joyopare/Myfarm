# Farm Marketplace - Django Web Application

A comprehensive Django-based marketplace connecting farmers directly with customers, featuring real-time messaging, advanced search, analytics, and secure payment processing.

## 🌟 Features

### Core Functionality
- **User Authentication**: Separate registration/login for customers and farmers
- **Product Management**: Full CRUD operations for farmers to manage their products
- **Shopping Cart & Orders**: Complete e-commerce functionality with order tracking
- **In-App Messaging**: Real-time communication between customers and farmers
- **Rating & Reviews**: Customer feedback system for farmers and products
- **Follow System**: Customers can follow their favorite farmers
- **Advanced Search**: Multi-criteria search with filters and sorting
- **Analytics Dashboard**: Comprehensive business insights for farmers
- **Payment Integration**: Stripe payment processing (ready for production)
- **Real-time Notifications**: WebSocket-based notification system

### Technical Features
- **Responsive Design**: Bootstrap 5 with mobile-first approach
- **AJAX Integration**: Seamless user experience without page reloads
- **Django Channels**: Real-time WebSocket communication
- **Admin Interface**: Comprehensive backend management
- **Security**: CSRF protection, user authentication, and data validation
- **Testing Suite**: Comprehensive test coverage

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Redis (for Django Channels)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Myfarm
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Create .env file
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   STRIPE_PUBLISHABLE_KEY=pk_test_your_key
   STRIPE_SECRET_KEY=sk_test_your_key
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   ```

5. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Load sample data (optional)**
   ```bash
   python create_sample_data.py
   ```

8. **Start Redis server**
   ```bash
   redis-server
   ```

9. **Run development server**
   ```bash
   python manage.py runserver
   ```

Visit `http://127.0.0.1:8000` to access the application.

## 📁 Project Structure

```
Myfarm/
├── accounts/              # User authentication & profiles
│   ├── models.py         # User, CustomerProfile, FarmerProfile
│   ├── views.py          # Registration, login, profile management
│   ├── forms.py          # User registration forms
│   └── admin.py          # Admin configurations
├── products/             # Product management
│   ├── models.py         # Product, Category, ProductReview
│   ├── views.py          # Product CRUD, search, analytics
│   ├── forms.py          # Product forms
│   └── admin.py          # Product admin
├── orders/               # Shopping cart & order processing
│   ├── models.py         # Cart, Order, OrderItem
│   ├── views.py          # Cart operations, checkout
│   ├── forms.py          # Checkout forms
│   └── payment.py        # Stripe payment processing
├── messaging/            # Real-time messaging & notifications
│   ├── models.py         # Conversation, Message, Notification
│   ├── views.py          # Messaging views
│   ├── consumers.py      # WebSocket consumers
│   └── routing.py        # WebSocket routing
├── templates/            # HTML templates
│   ├── accounts/         # User-related templates
│   ├── products/         # Product templates
│   ├── orders/           # Order templates
│   ├── messaging/        # Messaging templates
│   └── base.html         # Base template
├── static/               # Static files (CSS, JS, images)
├── media/                # User uploads
├── farmmarket/           # Main Django project
│   ├── settings.py       # Django settings
│   ├── urls.py           # URL routing
│   └── asgi.py           # ASGI configuration
├── requirements.txt      # Python dependencies
├── tests.py             # Test suite
└── manage.py            # Django management script
```

## 🎯 User Roles & Permissions  

### Customers
- Browse and search products
- Add items to cart and place orders
- Message farmers directly
- Rate and review farmers
- Follow favorite farmers
- View order history
- Manage profile

### Farmers
- Add and manage products
- View analytics dashboard
- Respond to customer messages
- View and manage orders
- Track sales performance
- Manage farm profile
- Upload verification documents

### Admin
- Manage all users and content
- Verify farmer accounts
- Monitor system activity
- Generate reports

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_key
STRIPE_SECRET_KEY=sk_test_your_stripe_key
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
REDIS_URL=redis://localhost:6379
```

### Database Configuration
The project uses SQLite by default. For production, configure PostgreSQL:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'farmmarket_db',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 🧪 Testing

Run the test suite:

```bash
python manage.py test
```

Run specific test modules:

```bash
python manage.py test accounts
python manage.py test products
python manage.py test orders
```

## 📊 Analytics & Monitoring

The application includes comprehensive analytics:

- **Sales Analytics**: Revenue tracking, order patterns
- **Product Performance**: Best-selling products, ratings
- **Customer Insights**: Demographics, behavior patterns
- **Real-time Metrics**: Live dashboard updates

Access analytics at `/products/analytics/` (farmers only).

## 🔒 Security Features

- **CSRF Protection**: All forms include CSRF tokens
- **User Authentication**: Secure login/logout system
- **Permission Checks**: Role-based access control
- **Input Validation**: Server-side form validation
- **File Upload Security**: Restricted file types and sizes
- **SQL Injection Prevention**: Django ORM protection

## 🚀 Deployment

### Production Checklist

1. **Environment Setup**
   ```bash
   DEBUG=False
   ALLOWED_HOSTS=['yourdomain.com']
   ```

2. **Static Files**
   ```bash
   python manage.py collectstatic
   ```

3. **Database Migration**
   ```bash
   python manage.py migrate --run-syncdb
   ```

4. **SSL Configuration**
   - Configure HTTPS
   - Update SECURE_SSL_REDIRECT settings

5. **Media Files**
   - Configure cloud storage (AWS S3, etc.)
   - Update MEDIA_URL and MEDIA_ROOT

### Docker Deployment

```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 API Documentation

### REST Endpoints

- `GET /products/search/` - Product search API
- `POST /orders/add-to-cart/{product_id}/` - Add item to cart
- `POST /orders/update-cart/{item_id}/` - Update cart item
- `POST /messaging/send-message/` - Send message
- `POST /accounts/follow-farmer/{farmer_id}/` - Follow/unfollow farmer

### WebSocket Endpoints

- `ws/notifications/{user_id}/` - Real-time notifications
- `ws/chat/{conversation_id}/` - Real-time messaging

## 🐛 Troubleshooting

### Common Issues

1. **Redis Connection Error**
   ```bash
   # Start Redis server
   redis-server
   ```

2. **Migration Issues**
   ```bash
   python manage.py makemigrations --empty appname
   python manage.py migrate --fake-initial
   ```

3. **Static Files Not Loading**
   ```bash
   python manage.py collectstatic --clear
   ```

4. **Permission Denied Errors**
   ```bash
   # Check file permissions
   chmod 755 manage.py
   ```

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Email: support@farmmarket.com
- Documentation: [Wiki](link-to-wiki)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Django Framework
- Bootstrap 5
- Chart.js for analytics
- Stripe for payments
- Redis for real-time features

---

**Built with ❤️ for connecting farmers and customers directly.**
