# 💰 Expenses Management Tracker

## 🎯 Overview
A **secure desktop application** built with Python Tkinter for tracking monthly expenses with **SDG-aligned financial insights**. This tool helps users monitor utility bills, categorized spending, and visualize trends to promote responsible consumption.

![Application Preview](https://via.placeholder.com/800x450/0F1E3A/EFEFEF?text=Expenses+Tracker+Screenshot)

## ✨ Key Features

### 🔐 **Security & Authentication**
- **Login system** with password hashing (SHA-256)
- Protected user sessions
- Secure logout functionality

### 📊 **Expense Tracking**
- **Monthly utility bills** (Water & Electricity)
- **Categorized spending** with 6 custom categories
- **Automatic total calculation**
- **SDG-aligned tips** for sustainable spending

### 🎨 **Visual Analytics**
- **Total Expense Trend** line graph
- **Breakdown Trend** visualization (Water/Electricity/Others)
- **Interactive charts** with Matplotlib integration
- **Dark theme** optimized for readability

### 🔄 **Data Management**
- **CRUD operations** (Create, Read, Update, Delete)
- **Sorting capabilities** by date, highest/lowest total
- **Transaction categorization** system
- **Month-to-month comparison** with warnings

### 💡 **SDG Integration**
- **Goal 6** (Clean Water) - Water conservation tips
- **Goal 7** (Affordable Energy) - Electricity saving strategies
- **Goal 12** (Responsible Consumption) - Spending awareness
- **Goal 13** (Climate Action) - Energy reduction advice

## 🚀 Installation

### Prerequisites
```bash
Python 3.8 or higher
pip package manager
```

### Step-by-Step Setup

1. **Clone/Download** the repository
2. **Install required packages**:
```bash
pip install tkinter matplotlib
```
3. **Run the application**:
```bash
python expenses_tracker.py
```

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **GUI Framework** | Tkinter |
| **Database** | SQLite3 |
| **Data Visualization** | Matplotlib |
| **Security** | Hashlib (SHA-256) |
| **Date Handling** | datetime |

## 📁 Database Schema

### **users** (Authentication)
- `id` - Primary Key
- `username` - Unique identifier
- `password_hash` - Securely hashed password

### **expenses** (Monthly Totals)
- `id` - Primary Key
- `month` - YYYY-MM format
- `water` - Water bill amount
- `electricity` - Electricity bill amount
- `others` - Total categorized spending
- `total` - Sum of all expenses

### **transactions** (Detailed Spending)
- `id` - Primary Key
- `month` - Reference to expenses.month
- `category` - Spending category
- `description` - Transaction details
- `amount` - Individual transaction value

## 🎨 User Interface

### **Login Screen** 🔒
- Clean authentication interface
- Password masking
- Error handling for invalid credentials

### **Main Dashboard** 📋
- **Left Panel**: Data entry and controls
- **Right Panel**: Expense table and graphs
- **Color-coded** buttons for different actions

### **Transaction Manager** 💳
- Add/edit/delete categorized expenses
- 6 predefined categories:
  - 🍎 Food & Groceries
  - 🚗 Transport
  - 🏥 Healthcare
  - 🌱 Sustainable Goods
  - 💸 Wasteful Spending
  - 🎬 Entertainment

### **Graphical Analysis** 📈
- **Line graphs** for trend visualization
- **Color-coded** data series
- **Interactive** display updates

## 🎮 How to Use

### 1. **Login**
```
Username: admin
Password: password123
```

### 2. **Add Monthly Expenses**
1. Enter month in `YYYY-MM` format
2. Input water and electricity bills
3. Click "💾 SAVE EXPENSES"

### 3. **Manage Categorized Spending**
1. Click "🔄 Manage Spending"
2. Add transactions with categories
3. Track detailed spending habits

### 4. **Analyze Trends**
- View "Total Trend" for overall spending
- Use "Breakdown Trend" for category analysis
- Sort data by different criteria

### 5. **Update/Delete Records**
- Select from table to edit
- Use "✏️ UPDATE RECORD" to modify
- "🗑️ DELETE SELECTED" to remove

## 🎯 SDG Features Integration

| SDG Goal | Implementation |
|----------|----------------|
| **Goal 6** | Water usage warnings & conservation tips |
| **Goal 7** | Electricity monitoring & efficiency suggestions |
| **Goal 12** | Responsible consumption tracking |
| **Goal 13** | Climate action through reduced energy use |

The application provides **personalized tips** when spending increases in specific categories, promoting sustainable financial habits aligned with UN Sustainable Development Goals.

## 🎨 Color Scheme

| Color | Hex | Usage |
|-------|-----|-------|
| Primary | `#0F1E3A` | Main background |
| Secondary | `#1B3A64` | Panels & frames |
| Accent | `#4DEAEF` | Buttons & highlights |
| Text | `#EFEFEF` | All text elements |
| Button | `#2D5A8E` | Action buttons |
| Delete | `#9E2A2B` | Delete operations |
| Manage | `#167A6E` | Transaction management |

## 🔒 Security Features

- **Password hashing** using SHA-256
- **SQL injection prevention** through parameterized queries
- **Session management** with proper logout
- **Input validation** on all fields

## 📊 Data Validation

- **Month format**: `YYYY-MM` validation
- **Currency input**: Peso symbol handling
- **Positive values**: No negative amounts
- **Duplicate prevention**: Unique month constraint

## 🚨 Warning System

The application provides **proactive warnings**:
- **Zero input detection** - Alerts for missing data
- **Spike warnings** - Notifies when expenses increase
- **SDG tips** - Sustainable spending advice
- **Save confirmation** - Prevents accidental deletions

## 🔧 Customization Options

### Modify Categories
Edit the `CATEGORIES` list in the code to add/remove spending categories:

```python
CATEGORIES = ['Food & Groceries', 'Transport', 'Healthcare',
              'Sustainable Goods', 'Wasteful Spending', 'Entertainment']
```

### Change Colors
Update the color constants at the top of the file:

```python
PRIMARY_COLOR = "#0F1E3A"
SECONDARY_COLOR = "#1B3A64"
ACCENT_COLOR = "#4DEAEF"
```

### Update SDG Tips
Modify the `SDG_TIPS` dictionary for customized advice:

```python
SDG_TIPS = {
    "water": "Your custom water saving tip here",
    # ... other categories
}
```

## 📦 File Structure

```
expenses_tracker.py     # Main application file
expenses_tracker.db     # SQLite database (auto-generated)
README.md              # This documentation
```

## 🐛 Troubleshooting

### Common Issues

1. **"Database is locked"**
   - Close all instances of the application
   - Delete the .db file and restart

2. **Graph not displaying**
   - Ensure matplotlib is installed: `pip install matplotlib`
   - Check Python version compatibility

3. **Login failing**
   - Default credentials: admin/password123
   - Database might be corrupted - delete and restart

### Error Messages
- **"Invalid month format"**: Use YYYY-MM (e.g., 2024-03)
- **"Already exists"**: Each month can only have one record
- **"No record selected"**: Click on a table row before editing/deleting

## 🔮 Future Enhancements

Planned features for upcoming versions:
- 💱 Multiple currency support
- 📱 Mobile companion app
- ☁️ Cloud backup functionality
- 🤖 AI-powered spending predictions
- 👥 Multi-user household support
- 📄 Export to PDF/Excel reports

## 👥 Target Users

- 🏠 **Households** tracking monthly expenses
- 🌱 **Eco-conscious individuals** monitoring resource usage
- 💼 **Small businesses** managing operational costs
- 🎓 **Students** learning financial literacy
- 📊 **Researchers** analyzing consumption patterns

## 📝 License & Attribution

This project is developed for **educational purposes** with a focus on:
- **Financial literacy** promotion
- **SDG awareness** integration
- **Practical Python application** development

### Credits
- **UN SDGs** for sustainable development framework
- **Python community** for excellent libraries
- **Tkinter** for robust GUI framework

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the code comments for specific functions
3. Ensure all dependencies are properly installed

---

## 🚀 Quick Start Command

```bash
# On first run, the database will be created automatically
# Default login credentials:
# Username: admin
# Password: password123

python expenses_tracker.py
```

---

**🌟 Remember**: Tracking expenses is the first step toward financial responsibility and sustainable living! This tool not only helps you save money but also contributes to global sustainability goals through conscious consumption.
