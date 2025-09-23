from decimal import Decimal

from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Vrac(models.Model):
    TYPE_CHOICES = [
        ("vrac", "Vrac"),
        ("unite", "Unité"),
    ]

    name = models.CharField(max_length=100)
    type = models.CharField(max_length=5, choices=TYPE_CHOICES)

    price = ArrayField(
        models.DecimalField(
            max_digits=10,
            decimal_places=2,
            validators=[MinValueValidator(Decimal("0.00"))],
        ),
        blank=True,
        default=list,
    )

    stock = ArrayField(
        models.IntegerField(
            validators=[
                MinValueValidator(0)]),
        blank=True,
        default=list)

    stock_available = ArrayField(
        models.IntegerField(
            validators=[
                MinValueValidator(0)]),
        blank=True,
        default=list)

    def __str__(self):
        return self.name

    def clean(self):
        if len(self.price) != len(self.stock) or len(self.stock) != len(
            self.stock_available
        ):
            raise ValidationError(
                "Les listes price, stock et stock_available doivent avoir la même taille"
            )

    def get_total_stock(self):
        """Retourne la somme totale des stocks"""
        return sum(self.stock) if self.stock else 0

    def get_total_stock_available(self):
        """Retourne la somme totale des stocks disponibles"""
        return sum(self.stock_available) if self.stock_available else 0

    def calculate_price(self, N):
        """
        Calcule le prix total pour une quantité N selon le type de produit
        Args:
            N: quantité en grammes si type='vrac', nombre d'unités si type='unite'
        Returns:
            float: prix total calculé arrondi à 2 décimales
            None: si la quantité demandée est supérieure au stock disponible
        """
        if N <= 0:
            return 0.0

        remaining = N
        total_price = 0.0
        quantity_factor = 1000 if self.type == "vrac" else 1

        if self.get_total_stock_available() < N:
            return None

        for price, available in zip(self.price, self.stock_available):
            if remaining <= 0:
                break

            quantity_from_this_batch = min(available, remaining)

            if self.type == "vrac":
                total_price += (price / quantity_factor) * \
                    quantity_from_this_batch
            else:
                total_price += price * quantity_from_this_batch

            remaining -= quantity_from_this_batch

        return round(total_price, 2)

    def reduce_stock(self, prices, quantities):
        """
        Réduit les stocks selon les prix et quantités données
        Args:
            prices: liste de prix à chercher
            quantities: liste des quantités à retirer
        Raises:
            ValidationError: si pas assez de stock ou si prix non trouvé
        """
        if len(prices) != len(quantities):
            raise ValidationError(
                "Les listes prices et quantities doivent avoir la même taille"
            )

        # Vérification préalable des stocks
        for price, quantity in zip(prices, quantities):
            try:
                idx = self.price.index(price)
                if self.stock[idx] < quantity:
                    raise ValidationError(
                        f"Stock insuffisant pour le prix {price}")
            except ValueError:
                raise ValidationError(f"Prix {price} non trouvé dans le stock")

        # Réduction des stocks
        indices_to_remove = []
        for price, quantity in zip(prices, quantities):
            idx = self.price.index(price)
            self.stock[idx] -= quantity

            # Si le stock tombe à 0, on marque l'index pour suppression
            if self.stock[idx] < 100:
                indices_to_remove.append(idx)

        # Suppression des éléments avec stock = 0 (en ordre décroissant pour ne
        # pas perturber les indices)
        for idx in sorted(indices_to_remove, reverse=True):
            self.price.pop(idx)
            self.stock.pop(idx)
            self.stock_available.pop(idx)

        self.save()

    def add_stock(self, prices, quantities):
        """
        Ajoute du stock avec de nouveaux prix
        Args:
            prices: liste des prix des nouveaux stocks
            quantities: liste des quantités à ajouter
        Raises:
            ValidationError: si les prix ou quantités sont invalides
        """
        if len(prices) != len(quantities):
            raise ValidationError(
                "Les listes prices et quantities doivent avoir la même taille"
            )

        # Vérification des valeurs
        for price, quantity in zip(prices, quantities):
            if price <= 0:
                raise ValidationError(f"Le prix {price} doit être positif")
            if quantity <= 0:
                raise ValidationError(
                    f"La quantité {quantity} doit être positive")

        # Ajout des nouveaux stocks
        for price, quantity in zip(prices, quantities):
            # Si le prix existe déjà, on ajoute au stock existant
            try:
                idx = self.price.index(price)
                self.stock[idx] += quantity
                self.stock_available[idx] += quantity
            # Sinon, on crée une nouvelle entrée
            except ValueError:
                self.price.append(price)
                self.stock.append(quantity)
                self.stock_available.append(quantity)

        self.save()

    def reduce_stock_available(self, prices, quantities):
        """
        Réduit uniquement le stock disponible
        Args:
            prices: liste de prix à chercher
            quantities: liste des quantités à retirer
        Raises:
            ValidationError: si pas assez de stock disponible, si prix non trouvé ou si listes invalides
        """
        if len(prices) != len(quantities):
            raise ValidationError(
                "Les listes prices et quantities doivent avoir la même taille"
            )

        # Vérification préalable des stocks
        for price, quantity in zip(prices, quantities):
            try:
                idx = self.price.index(price)
                if self.stock_available[idx] < quantity:
                    raise ValidationError(
                        f"Stock disponible insuffisant pour le prix {price}"
                    )
            except ValueError:
                raise ValidationError(f"Prix {price} non trouvé dans le stock")

        # Réduction des stocks disponibles
        for price, quantity in zip(prices, quantities):
            idx = self.price.index(price)
            self.stock_available[idx] -= quantity

        self.save()

    def add_stock_available(self, prices, quantities):
        """
        Ajoute uniquement du stock disponible
        Args:
            prices: liste des prix des stocks
            quantities: liste des quantités à ajouter
        Raises:
            ValidationError: si prix non trouvé, quantités invalides ou stock dépassé
        """
        if len(prices) != len(quantities):
            raise ValidationError(
                "Les listes prices et quantities doivent avoir la même taille"
            )

        # Vérification des valeurs et existence des prix
        for price, quantity in zip(prices, quantities):
            if quantity <= 0:
                raise ValidationError(
                    f"La quantité {quantity} doit être positive")
            try:
                idx = self.price.index(price)
                if self.stock_available[idx] + quantity > self.stock[idx]:
                    raise ValidationError(
                        f"Le stock disponible ne peut pas dépasser le stock total pour le prix {price}"
                    )
            except ValueError:
                raise ValidationError(f"Prix {price} non trouvé dans le stock")

        # Ajout des stocks disponibles
        for price, quantity in zip(prices, quantities):
            idx = self.price.index(price)
            self.stock_available[idx] += quantity

        self.save()

    def update_quantity(self, quantity):
        """
        Met à jour la quantité disponible pour un prix donné
        Args:
            price: prix à chercher
            quantity: nouvelle quantité
        Raises:
            ValidationError: si le prix n'est pas trouvé ou si la quantité est invalide
        """
        if quantity < self.get_total_stock() - self.get_total_stock_available():
            raise ValidationError(
                "Problème de stock, pas assez de stock disponible pour gérer les commandes"
            )
        else:
            quantity -= self.get_total_stock()
            if quantity < 0:  # Perte de stock
                for i in range(len(self.stock)):
                    if self.stock_available[i] > 0:
                        reduce = min(self.stock_available[i], -1 * quantity)
                        self.reduce_stock_available([self.price[i]], [reduce])
                        self.reduce_stock([self.price[i]], [reduce])
                        quantity += reduce
                        if quantity == 0:
                            break
            if quantity > 0:
                self.add_stock([self.price[0]], [quantity])
                self.add_stock_available([self.price[0]], [quantity])

        self.save()


class OrderItem(models.Model):
    """Intermediate model to link Order and Vrac with additional data"""

    order = models.ForeignKey("Order", on_delete=models.CASCADE)
    vrac = models.ForeignKey("Vrac", on_delete=models.CASCADE)
    prices = ArrayField(
        models.DecimalField(
            max_digits=10,
            decimal_places=2,
            validators=[MinValueValidator(Decimal("0.00"))],
        ),
        blank=True,
        default=list,
    )
    quantities = ArrayField(
        models.IntegerField(
            validators=[
                MinValueValidator(0)]),
        blank=True,
        default=list)

    def __str__(self):
        return f"Commande de {self.order.name} / {self.vrac.name}"

    def clean(self):
        if len(self.prices) != len(self.quantities):
            raise ValidationError(
                "Les listes prices et quantities doivent avoir la même taille"
            )
        # Verify that prices exist in Vrac
        for price in self.prices:
            if price not in self.vrac.price:
                raise ValidationError(
                    f"Le prix {price} n'existe pas pour le produit {self.vrac.name}"
                )


class Order(models.Model):
    name = models.CharField(max_length=100)
    id_user = models.IntegerField(default=-1)
    products = models.ManyToManyField(
        Vrac, through="OrderItem", related_name="orders")

    def __str__(self):
        return f"Commande de {self.name}"

    def get_total_price(self):
        """
        Calcule le prix total de la commande
        Returns:
            Decimal: prix total calculé arrondi à 2 décimales
        """
        total_price = Decimal("0.00")

        for item in self.orderitem_set.all():
            # Get the price based on product type
            if item.vrac.type == "vrac":
                # For vrac products, divide by 1000 to convert from price/kg to
                # price/g
                item_total = sum(
                    (price / Decimal("1000")) * quantity
                    for price, quantity in zip(item.prices, item.quantities)
                )
            else:
                # For unite products, use price directly
                item_total = sum(
                    price * quantity
                    for price, quantity in zip(item.prices, item.quantities)
                )
            total_price += item_total

        return round(total_price, 2)


class Bike(models.Model):
    name = models.CharField(max_length=50)
    is_borrowed = models.BooleanField(default=False)
    borrower_id = models.IntegerField(default=-1)

    def __str__(self):
        return self.name.__str__()


class RequestForm(models.Model):
    SERVICE_CHOICES = [
        ("velos", "Vélos"),
        ("vracs", "Vracs"),
        ("musique", "Musique"),
        ("ki", "KI"),
        ("med", "Med"),
        ("bde", "BDE"),
        ("bds", "BDS"),
        ("bda", "BDA"),
        ("foyer", "Foyer"),
        ("pep", "PEP"),
        ("jardin", "Jardin"),
        ("dvp", "DVP"),
        ("trium", "Trium"),
        ("bitum", "Bitum"),
    ]

    STATUS_CHOICES = [
        ("pending", "En attente"),
        ("done", "Lue"),
    ]

    name = models.CharField(max_length=100)
    message = models.TextField()
    service = models.CharField(max_length=10, choices=SERVICE_CHOICES)
    status = models.CharField(
        max_length=10,
        default="pending",
        choices=STATUS_CHOICES)

    def __str__(self):
        return self.name

    def mark_as_done(self):
        """
        Change the status from 'pending' to 'done'
        """
        if self.status == "pending":
            self.status = "done"
            self.save()


class ReservationBike(models.Model):
    """
    Logs of bike reservations
    """

    bike = models.ForeignKey(Bike, on_delete=models.CASCADE)
    borrower_id = models.IntegerField(default=-1)
    name = models.CharField(max_length=100)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)  # Null if ongoing

    def __str__(self):
        end_date_str = (self.end_date.strftime(
            "%Y-%m-%d %H:%M:%S") if self.end_date else "Ongoing")
        return f"Réservation de {self.bike.name} par {self.name} - Start: {self.start_date.strftime('%Y-%m-%d %H:%M:%S')}, End: {end_date_str}"


class ReservationMusicRoom(models.Model):
    """
    Logs of music room reservations
    """

    borrower_id = models.IntegerField(default=-1)
    name = models.CharField(max_length=100)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def __str__(self):
        return f"Réservation de salle de musique par {self.borrower_id} - Start: {self.start_date.strftime('%Y-%m-%d %H:%M:%S')}, End: {self.end_date.strftime('%Y-%m-%d %H:%M:%S')}"


class Mediatek(models.Model):
    is_open = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if Mediatek.objects.exists() and not self.pk:
            raise ImproperlyConfigured("Only one Mediatek instance allowed")
        super(Mediatek, self).save(*args, **kwargs)

    def __str__(self):
        return "Med ouverte" if self.is_open else "Med fermée"

    def open(self):
        self.is_open = True
        self.save()

    def close(self):
        self.is_open = False
        self.save()


class MedItem(models.Model):
    TYPE_CHOICES = [
        ("roman", "Roman"),
        ("manga", "Manga"),
        ("bd", "Bande dessinée"),
        ("jeu", "Jeu"),
    ]
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    year = models.IntegerField(blank=True, null=True)
    is_available = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="media", blank=True)
    borrowed_by = models.IntegerField(default=-1)
    borrowed_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} ({self.type}) - {self.author} - {self.year}"

    def borrow(self, borrower_id):
        if not self.is_available:
            raise ValidationError("Item not available")
        self.is_available = False
        self.borrowed_by = borrower_id
        self.borrowed_date = timezone.now()
        self.save()

    def return_item(self):
        self.is_available = True
        self.borrowed_by = -1
        self.borrowed_date = None
        self.save()


class Local(models.Model):
    TYPE_CHOICES = [
        ("med", "Médiathèque"),
        ("ki", "KI"),
        ("musique", "Salle de musique"),
        ("bde", "BDE"),
        ("bds", "BDS"),
        ("bda", "BDA"),
        ("foyer", "Foyer"),
        ("pep", "PEP"),
        ("jardin", "Jardin"),
        ("dvp", "DVP"),
        ("trium", "Trium"),
        ("bitum", "Bitum"),
    ]

    name = models.CharField(max_length=50, choices=TYPE_CHOICES, unique=True)
    is_open = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        # Ensure only one instance per local type
        if Local.objects.filter(name=self.name).exists() and not self.pk:
            raise ImproperlyConfigured(
                f"Only one {self.get_name_display()} instance allowed"
            )
        super(Local, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_name_display()} - {'ouvert' if self.is_open else 'fermé'}"

    def open(self):
        self.is_open = True
        self.save()

    def close(self):
        self.is_open = False
        self.save()
