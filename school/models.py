from django.db import models

CLASS_YEARS = [
    ('S1', 'Senior 1'),
    ('S2', 'Senior 2'),
    ('S3', 'Senior 3'),
    ('S4', 'Senior 4'),
    ('S5', 'Senior 5'),
    ('S6', 'Senior 6'),
]

class Subject(models.Model):
    name = models.CharField(max_length=100)
    level = models.CharField(max_length=1, choices=[('O', 'O Level'), ('A', 'A Level')])
    is_subsidiary = models.BooleanField(default=False)  # New field for GP, Sub Maths, Sub ICT

    def __str__(self):
        return f"{self.name} ({self.level})"

class Student(models.Model):
    student_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    level = models.CharField(max_length=1, choices=[('O', 'O Level'), ('A', 'A Level')])
    class_year = models.CharField(max_length=2, choices=CLASS_YEARS)
    combination = models.CharField(max_length=50, blank=True, null=True)
    subjects = models.ManyToManyField(Subject, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.class_year in ['S1', 'S2', 'S3', 'S4']:
            self.level = 'O'
        elif self.class_year in ['S5', 'S6']:
            self.level = 'A'
        super().save(*args, **kwargs)

    def total_points(self):
        if self.level != 'A':
            return None
        principal_results = self.result_set.filter(subject__is_subsidiary=False)[:3]  # Up to 3 principals
        subsidiary_results = self.result_set.filter(subject__is_subsidiary=True)[:2]  # Up to 2 subsidiaries
        total = sum(result.get_points() or 0 for result in principal_results)
        total += sum(result.get_points() or 0 for result in subsidiary_results)
        return min(total, 20)  # Cap at 20 points

class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    score = models.IntegerField()

    def __str__(self):
        return f"{self.student.name} - {self.subject.name}: {self.score}"

    def get_grade(self):
        if self.student.level == 'O':  # O'Level UCE (assumed ranges)
            if self.score >= 80:
                return 'A'  # Exceptional
            elif self.score >= 70:
                return 'B'  # Outstanding
            elif self.score >= 60:
                return 'C'  # Satisfactory
            elif self.score >= 50:
                return 'D'  # Basic
            elif self.score >= 40:
                return 'E'  # Elementary
            else:
                return 'F'  # Fail (not certified)
        else:  # A'Level UACE
            if self.score >= 80:
                return 'A'
            elif self.score >= 70:
                return 'B'
            elif self.score >= 60:
                return 'C'
            elif self.score >= 50:
                return 'D'
            elif self.score >= 40:
                return 'E'
            elif self.score >= 35:
                return 'O'
            else:
                return 'F'

    def get_points(self):
        if self.student.level != 'A':
            return None
        if self.subject.is_subsidiary:
            return 1 if self.score >= 50 else 0
        grade = self.get_grade()
        if grade == 'A': return 6
        elif grade == 'B': return 5
        elif grade == 'C': return 4
        elif grade == 'D': return 3
        elif grade == 'E': return 2
        elif grade == 'O': return 1
        else: return 0