
# class RefreshToken(Base):
#     __tablename__ = "refresh_tokens"

#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
#     token_hash = Column(String(255), nullable=False)
#     revoked = Column(Boolean, default=False)
#     created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
#     expires_at = Column(DateTime, nullable=False)
#     replaced_by_token = Column(UUID(as_uuid=True), nullable=True)  # points to new token if rotated