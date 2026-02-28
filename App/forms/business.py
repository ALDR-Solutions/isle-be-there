from App.controllers.base import get_caribbean_countries
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import IntegerField, StringField, SubmitField, BooleanField, SelectField, TextAreaField, EmailField
from wtforms.validators import DataRequired, Email, Length, Optional, Regexp


class ListingForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    street=StringField('Street', validators=[DataRequired()])
    city=StringField('City', validators=[DataRequired()])   
    state=StringField('State', validators=[DataRequired()])
    country=SelectField('Country', choices=[], validators=[DataRequired()])
    postal_code=StringField('Zip Code', validators=[DataRequired()])
    latitude=StringField('Latitude', validators=[DataRequired()])
    longitude=StringField('Longitude', validators=[DataRequired()])
    phone_number=StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15), # Adjust length as needed
        Regexp(r'^[+]*[(]{0,1}[0-9]{1,4}[)]{0,1}[-\s\./0-9]*$', message="Invalid phone number format")])
    email_address=EmailField('Email Address', validators=[DataRequired(), Email()]) 
    image_urls=FileField('Image URL', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')], render_kw={"multiple": True})
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.country.choices = get_caribbean_countries()

class AddRestaurantListingForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])

    street=StringField('Street', validators=[DataRequired()])
    city=StringField('City', validators=[DataRequired()])   
    state=StringField('State', validators=[DataRequired()])
    country=StringField('Country', validators=[DataRequired()])
    postal_code=StringField('Zip Code', validators=[DataRequired()])
    latitude=StringField('Latitude', validators=[DataRequired()])
    longitude=StringField('Longitude', validators=[DataRequired()])

    image_url=StringField('Image URL', validators=[DataRequired()])
    cuisine_type=SelectField('Cuisine Type', choices=[('italian', 'Italian'), ('chinese', 'Chinese'), ('indian', 'Indian'), ('mexican', 'Mexican'), ('american', 'American')], validators=[DataRequired()])
    seating_capacity=IntegerField('Seating Capacity', validators=[DataRequired()])
    opening_time=StringField('Opening Time (HH:MM)', validators=[DataRequired()])
    closing_time=StringField('Closing Time (HH:MM)', validators=[DataRequired()])

    age_requirement = IntegerField('Age Requirement', validators=[DataRequired()])
    reservation_required = BooleanField('Reservation Required',default=False)
    cancellation_policy = StringField('Cancellation Policy', validators=[DataRequired()])
    status = BooleanField('Open for Reserations', default=True)
    takeout_available = BooleanField('Takeout Available', default=True)
    facilites = StringField('Facilities (comma separated)', validators=[DataRequired()])

    submit = SubmitField('Add Restaurant Listing')

#addinfg a tour company listing by business user

class AddTourListingForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])

    street=StringField('Street', validators=[DataRequired()])
    city=StringField('City', validators=[DataRequired()])   
    state=StringField('State', validators=[DataRequired()])
    country=StringField('Country', validators=[DataRequired()])
    postal_code=StringField('Zip Code', validators=[DataRequired()])
    latitude=StringField('Latitude', validators=[DataRequired()])
    longitude=StringField('Longitude', validators=[DataRequired()])

    image_url=StringField('Image URL', validators=[DataRequired()])
    status = BooleanField('Available for Booking', default=True)
    highlights = TextAreaField('Tour Highlights', validators=[DataRequired()])

    schedule=TextAreaField('Schedule Details', validators=[DataRequired()])
    submit = SubmitField('Add Tour Listing')


class AddActivityListingForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])

    street=StringField('Street', validators=[DataRequired()])
    city=StringField('City', validators=[DataRequired()])   
    state=StringField('State', validators=[DataRequired()])
    country=StringField('Country', validators=[DataRequired()])
    postal_code=StringField('Zip Code', validators=[DataRequired()])
    latitude=StringField('Latitude', validators=[DataRequired()])
    longitude=StringField('Longitude', validators=[DataRequired()])

    image_url=StringField('Image URL', validators=[DataRequired()])
    status = BooleanField('Available for Booking', default=True)
    safety_measures = TextAreaField('Safety Measures', validators=[DataRequired()])

    submit = SubmitField('Add Activity Listing')





# editing a hotel listing by business user
class EditHotelListingForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])

    street=StringField('Street', validators=[DataRequired()])
    city=StringField('City', validators=[DataRequired()])   
    state=StringField('State', validators=[DataRequired()])
    country=StringField('Country', validators=[DataRequired()])
    postal_code=StringField('Zip Code', validators=[DataRequired()])
    latitude=StringField('Latitude', validators=[DataRequired()])
    longitude=StringField('Longitude', validators=[DataRequired()])

    image_url=StringField('Image URL')
    # official star rating, not platform specific rating (generated from user reviews)
    star_rating=SelectField('Star Rating', choices=[('1', '1 Star'), ('2', '2 Stars'), ('3', '3 Stars'), ('4', '4 Stars'), ('5', '5 Stars')], validators=[DataRequired()])
    hotel_type=SelectField('Hotel Type', choices=[('luxury', 'Luxury'), ('boutique', 'Boutique'), ('budget', 'Budget'), ('economy', 'economy')], validators=[DataRequired()])
    room_count=IntegerField('Room Count', validators=[DataRequired()])
    available_rooms=IntegerField('Available Rooms', validators=[DataRequired()])
    amenities = StringField('Amenities (comma separated)', validators=[DataRequired()])
    nearby_attractions = StringField('Nearby Attractions (comma separated)', validators=[DataRequired()])

    age_requirement = IntegerField('Age Requirement', validators=[DataRequired()])
    deposit_required = BooleanField('Deposit Required')
    cancellation_policy = StringField('Cancellation Policy', validators=[DataRequired()])
    status = BooleanField('Open for Booking', default=True)
    last_renovation_date = StringField('Last Renovation Date (YYYY-MM-DD)', validators=[DataRequired()])

    submit = SubmitField('Update Hotel Listing')

# editing a restaurant listing by business user
class EditRestaurantListingForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])

    street=StringField('Street', validators=[DataRequired()])
    city=StringField('City', validators=[DataRequired()])   
    state=StringField('State', validators=[DataRequired()])
    country=StringField('Country', validators=[DataRequired()])
    postal_code=StringField('Zip Code', validators=[DataRequired()])
    latitude=StringField('Latitude', validators=[DataRequired()])
    longitude=StringField('Longitude', validators=[DataRequired()])

    image_url=StringField('Image URL', validators=[DataRequired()])
    cuisine_type=SelectField('Cuisine Type', choices=[('italian', 'Italian'), ('chinese', 'Chinese'), ('indian', 'Indian'), ('mexican', 'Mexican'), ('american', 'American')], validators=[DataRequired()])
    seating_capacity=IntegerField('Seating Capacity', validators=[DataRequired()])
    opening_time=StringField('Opening Time (HH:MM)', validators=[DataRequired()])
    closing_time=StringField('Closing Time (HH:MM)', validators=[DataRequired()])

    age_requirement = IntegerField('Age Requirement', validators=[DataRequired()])
    reservation_required = BooleanField('Reservation Required',default=False)
    cancellation_policy = StringField('Cancellation Policy', validators=[DataRequired()])
    status = BooleanField('Open for Reserations', default=True)
    takeout_available = BooleanField('Takeout Available', default=True)
    facilites = StringField('Facilities (comma separated)', validators=[DataRequired()])

    submit = SubmitField('Update Restaurant Listing')


# editing an activity listing by business user
class EditActivityListingForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])

    street=StringField('Street', validators=[DataRequired()])
    city=StringField('City', validators=[DataRequired()])   
    state=StringField('State', validators=[DataRequired()])
    country=StringField('Country', validators=[DataRequired()])
    postal_code=StringField('Zip Code', validators=[DataRequired()])
    latitude=StringField('Latitude', validators=[DataRequired()])
    longitude=StringField('Longitude', validators=[DataRequired()])

    image_url=StringField('Image URL', validators=[DataRequired()])
    status = BooleanField('Available for Booking', default=True)
    safety_measures = TextAreaField('Safety Measures', validators=[DataRequired()])

    submit = SubmitField('Update Activity Listing')

# editing a tour listing by business user
class EditTourListingForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])

    street=StringField('Street', validators=[DataRequired()])
    city=StringField('City', validators=[DataRequired()])   
    state=StringField('State', validators=[DataRequired()])
    country=StringField('Country', validators=[DataRequired()])
    postal_code=StringField('Zip Code', validators=[DataRequired()])
    latitude=StringField('Latitude', validators=[DataRequired()])
    longitude=StringField('Longitude', validators=[DataRequired()])

    image_url=StringField('Image URL', validators=[DataRequired()])
    status = BooleanField('Available for Booking', default=True)
    highlights = TextAreaField('Tour Highlights', validators=[DataRequired()])

    schedule=TextAreaField('Schedule Details', validators=[DataRequired()])
    submit = SubmitField('Edit Tour Listing')


#adding the hotel 

class AddHotelServiceForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    room_type = SelectField('Room Type', choices=[('single', 'Single'), ('double', 'Double'), ('suite', 'Suite')], validators=[DataRequired()])
    bed_count = IntegerField('Number of Beds', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = IntegerField('Price', validators=[DataRequired()])
    seasonal_price= IntegerField('Seasonal Price', validators=[DataRequired()])
    currency = StringField('Currency', validators=[DataRequired()])
    duration = IntegerField('Duration (in dnights)', validators=[DataRequired()])
    capacity = IntegerField('Maximum Guests Allowed', validators=[DataRequired()])

    #should be a dropdown to select from existing listings by the business user
    listing_id = SelectField('Listing', coerce=int, validators=[DataRequired()])
    image_url=StringField('Image URL', validators=[DataRequired()])
    
    submit = SubmitField('Add Service')


# adding dishes 
class AddRestaurantServiceForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = IntegerField('Price', validators=[DataRequired()])
    currency = StringField('Currency', validators=[DataRequired()])
    category = SelectField('Category', choices=[('appetizer', 'Appetizer'), ('main_course', 'Main Course'), ('dessert', 'Dessert'), ('beverage', 'Beverage')], validators=[DataRequired()])

    #should be a dropdown to select from existing listings by the business user
    listing_id = SelectField('Listing', coerce=int, validators=[DataRequired()])

    image_url=StringField('Image URL', validators=[DataRequired()])
    notes = TextAreaField('Special Notes', validators=[Optional()])


    submit = SubmitField('Add Dish')


# adding activities
class AddActivityServiceForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = IntegerField('Price', validators=[DataRequired()])
    currency = StringField('Currency', validators=[DataRequired()])
    capacity = IntegerField('Maximum Participants Allowed', validators=[DataRequired()])

    #should be a dropdown to select from existing listings by the business user
    listing_id = SelectField('Listing', coerce=int, validators=[DataRequired()])

    image_url=StringField('Image URL', validators=[DataRequired()])
    equipment_needed = TextAreaField('Equipment Needed', validators=[Optional()])
    activity_type=SelectField('Activity Type', choices=[('outdoor', 'Outdoor'), ('indoor', 'Indoor'), ('creative', 'Creative')], validators=[DataRequired()])
    duration=IntegerField('Duration (in hours)', validators=[DataRequired()])
    difficulty_level=SelectField('Difficulty Level', choices=[('easy', 'Easy'), ('moderate', 'Moderate'), ('advanced', 'Advanced')], validators=[DataRequired()])
    age_requirement = IntegerField('Age Requirement', validators=[DataRequired()])
    equipment_provided = BooleanField('Equipment Provided')
    waiver_required = BooleanField('Waiver Required')
    cancellation_policy = TextAreaField('Cancellation Policy', validators=[DataRequired()])
    submit = SubmitField('Add Activity')

# adding tours
class AddTourServiceForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = IntegerField('Price', validators=[DataRequired()])
    currency = StringField('Currency', validators=[DataRequired()])
    capacity = IntegerField('Maximum Participants Allowed', validators=[DataRequired()])

    #should be a dropdown to select from existing listings by the business user
    listing_id = SelectField('Listing', coerce=int, validators=[DataRequired()])
    tour_type=SelectField('Tour Type', choices=[('adventure', 'Adventure'), ('cultural', 'Cultural'), ('historical', 'Historical'), ('nature', 'Nature')], validators=[DataRequired()])
    duration=IntegerField('Duration (in hours)', validators=[DataRequired()])

    age_requirement = IntegerField('Age Requirement', validators=[DataRequired()])
    deposit_required = BooleanField('Deposit Required')
    cancellation_policy = TextAreaField('Cancellation Policy', validators=[DataRequired()])   

    submit = SubmitField('Add Tour')
