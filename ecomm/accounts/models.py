
from django.db import models
from django.contrib.auth.models import User
from base.models import BaseModel
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
from base.emails import send_account_activation_email
from products.models import Product, ColorVariant, SizeVariant
#each instance of this model is related to one and only one instance of the User model, and vice versa.
#It's similar to a primary key relationship, but in this case, it sets up a one-to-one link between the two models.
#1 user has 1 profile and vice-versa, models.CASCADE means that when the referenced User instance is deleted, the related instance of this model will also be deleted.
#related_name="profile": This argument sets the name for the reverse relationship from the User model back to this model. This means you can access the related profile from a user instance using user.profile
class Profile(BaseModel):
    user = models.OneToOneField(User , on_delete=models.CASCADE , related_name="profile")
    is_email_verified = models.BooleanField(default=False)
    email_token = models.CharField(max_length=100 , null=True , blank=True)
    profile_image = models.ImageField(upload_to = 'profile')

    def get_cart_count(self):
        return CartItems.objects.filter(cart__is_paid = False, cart__user = self.user).count()

class Cart(BaseModel):
    user = models.ForeignKey(User , on_delete=models.CASCADE , related_name="carts")
    is_paid = models.BooleanField(default=False)
    razor_pay_order_id = models.CharField(max_length=100 , null=True , blank=True)
    razor_pay_payment_id = models.CharField(max_length=100 , null=True , blank=True)
    razor_pay_payment_signature = models.CharField(max_length=100 , null=True , blank=True)

    def get_cart_total(self):
        cart_items = self.cart_items.all()
        price = []
        for cart_item in cart_items:
            price.append(cart_item.product.price)
            if cart_item.color_variant:
                color_variant_price = self.color_variant.price
                price.append(color_variant_price)
            if cart_item.size_variant:
                size_variant_price = cart_item.size_variant.price
                price.append(size_variant_price)
        return sum(price)

class CartItems(BaseModel):
    cart = models.ForeignKey(Cart , on_delete=models.CASCADE , related_name="cart_items")
    product = models.ForeignKey(Product , on_delete=models.SET_NULL , null=True, blank=True)
    color_variant = models.ForeignKey(ColorVariant , on_delete=models.SET_NULL , null=True, blank=True)
    size_variant = models.ForeignKey(SizeVariant , on_delete=models.SET_NULL , null=True, blank=True)

    def get_product_price(self):
        price = [self.product.price]

        if self.color_variant:
            color_variant_price = self.color_variant.price
            price.append(color_variant_price)
        if self.size_variant:
            size_variant_price = self.size_variant.price
            price.append(size_variant_price)
        return sum(price)
            
#@receiver: This decorator is used to register a function as a receiver for a signal,post_save: This is the signal that is sent at the end of the save method of a model. It indicates that a model instance has been saved,sender=User: This specifies that the signal should only be handled when it is sent by the User model.
#sender: The model class that sent the signal (in this case, the User model),instance: The actual instance of the model that was saved,created: A boolean that is True if a new record was created, and False if an existing record was updated.
#when request is sent by User model and after the instance is saved and if it is newly created than create profile object and send acitvation mail
@receiver(post_save , sender = User)
def  send_email_token(sender , instance , created , **kwargs):
    try:
        if created:
            email_token = str(uuid.uuid4())
            Profile.objects.create(user = instance , email_token = email_token)
            email = instance.email
            send_account_activation_email(email , email_token)

    except Exception as e:
        print(e)

