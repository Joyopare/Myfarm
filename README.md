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

4. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Load sample data (optional)**
   ```bash
   python create_sample_data.py
   ```

7. **Start Redis server**
   ```bash
   redis-server
   ```

8. **Run development server**
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


## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request



## 📞 Support

For support and questions:
- Create an issue on GitHub
- Email: oparejoy05@gmail.com


## 🙏 Acknowledgments

- Django Framework
- Bootstrap 5
- Chart.js for analytics
- Stripe for payments
- Redis for real-time features

---

**Built with ❤️ for connecting farmers and customers directly.**
