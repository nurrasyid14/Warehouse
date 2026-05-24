class ClusterMetrics:
    def __init__ (self, data, labels):
        self.data = data
        self.labels = labels
    def silhouette_score(self):        
        from sklearn.metrics import silhouette_score
        return silhouette_score(self.data, self.labels)
    
    