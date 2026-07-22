from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.support.models import ActivityLog, Complaint
import random


class Command(BaseCommand):
    help = 'Load sample activity and complaint data for demonstration'

    def handle(self, *args, **options):
        # Clear existing data
        ActivityLog.objects.all().delete()
        Complaint.objects.all().delete()

        # Sample activity logs for the last 7 days
        actions = [
            ('order_created', 'Orden creada', 'order', list(range(1, 15))),
            ('order_completed', 'Orden completada', 'order', list(range(1, 10))),
            ('reservation_created', 'Reserva creada', 'reservation', list(range(1, 8))),
            ('reservation_updated', 'Reserva actualizada', 'reservation', list(range(1, 5))),
            ('login', 'Acceso', 'user', []),
        ]

        now = timezone.now()
        emails = ['cliente1@test.com', 'cliente2@test.com', 'admin@gustos.com', 'manager@gustos.com', 'sistema@gustos.com']
        ips = ['192.168.1.100', '192.168.1.101', '10.0.0.50', '203.0.113.42', '127.0.0.1']

        created_count = 0
        for day_offset in range(7, -1, -1):
            log_time = now - timedelta(days=day_offset)

            for action, label, resource_type, resource_ids in actions:
                # 2-5 logs per action per day
                for _ in range(random.randint(2, 5)):
                    log_time = log_time + timedelta(hours=random.randint(1, 4), minutes=random.randint(0, 59))

                    resource_id = None
                    if resource_ids:
                        resource_id = random.choice(resource_ids)

                    ActivityLog.objects.create(
                        action=action,
                        user_email=random.choice(emails),
                        resource_type=resource_type,
                        resource_id=resource_id,
                        ip_address=random.choice(ips),
                        details={'demo': True},
                        created_at=log_time,
                    )
                    created_count += 1

        # Sample complaints
        complaint_subjects = [
            'Plato llegó frío',
            'Tiempo de espera largo',
            'Calidad del servicio',
            'Falta de variedad en menú',
            'Problema con reserva',
            'Atención deficiente',
        ]

        complaint_descriptions = {
            'Plato llegó frío': 'El lomo saltado llegó tibia y sin el sabor que esperaba. Se me pidió que lo consumiera así.',
            'Tiempo de espera largo': 'Esperé 45 minutos por mi pedido cuando la sala estaba semivacía.',
            'Calidad del servicio': 'El mozo fue grosero y no se interesó por satisfacer mis necesidades.',
            'Falta de variedad en menú': 'Siempre hay los mismos platillos. Quisiera ver más opciones de postres.',
            'Problema con reserva': 'Hice reserva a las 7pm pero me dijeron que no había mesa.',
            'Atención deficiente': 'Tuve que esperar 20 minutos para que alguien me atienda al llegar.',
        }

        statuses = ['new', 'in_progress', 'resolved', 'closed']
        responses = {
            'Nos disculpamos por el inconveniente. Implementaremos controles de temperatura en cocina.',
            'Revisaremos nuestros procesos para mejorar los tiempos. Gracias por tu paciencia.',
            'Reentrenaremos al personal sobre atención al cliente. Tu retroalimentación es valiosa.',
            'Evaluaremos agregar más opciones al menú. Apreciamos tu sugerencia.',
            'Verificaremos el sistema de reservas. Te ofrecemos un descuento en tu próxima visita.',
        }

        for i, subject in enumerate(complaint_subjects):
            status = random.choice(statuses)
            complaint = Complaint.objects.create(
                name=f'Cliente Ejemplo {i + 1}',
                email=f'cliente{i+1}@example.com',
                phone=f'98{random.randint(1000000, 9999999)}',
                subject=subject,
                description=complaint_descriptions[subject],
                status=status,
                response=random.choice(list(responses)) if status in ['resolved', 'closed'] else '',
                created_at=now - timedelta(days=random.randint(1, 7)),
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'✓ Loaded {created_count} activity logs and {len(complaint_subjects)} sample complaints'
            )
        )
