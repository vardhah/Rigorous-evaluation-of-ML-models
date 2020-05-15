from scripts.perception.perception_trainer import PerceptionTrainer

trainer = PerceptionTrainer(data_path='../data/perception', split='training', epoch=100)
model = trainer.fit()
trainer.save_model("./models/perception/")