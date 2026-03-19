"""
中等强国智能体

对应 PowerTier.MIDDLE_POWER (0.5 < z ≤ 1.5, 约24.17%)
不需要配置 leader_type

特点：
- 多边合作与平衡外交
- 在多边机制中发挥作用
- 推动议题设置和议程
- 在大国间保持平衡
- 提升国际地位和影响力

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from typing import Dict, List, Optional, Any
from datetime import datetime

from domain.agents.base_agent import BaseAgent


class DiplomaticStrategy:
    """
    外交策略

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(self, agent: Any):
        """
        初始化外交策略

        Args:
            agent: 中等强国智能体实例
        """
        self.agent = agent
        self._diplomatic_initiatives = []

    def assess_diplomatic_opportunities(self, global_data: Dict) -> Dict:
        """
        评估外交机会

        Args:
            global_data: 全球数据

        Returns:
            外交机会评估
        """
        # 评估多边机制参与机会
        multilateral_opportunities = self._assess_multilateral_opportunities(global_data)

        # 评估议题设置机会
        agenda_setting_opportunities = self._assess_agenda_setting_opportunities(global_data)

        # 评估大国平衡空间
        great_power_balance_space = self._assess_great_power_balance_space(global_data)

        return {
            "multilateral_opportunities": multilateral_opportunities,
            "agenda_setting_opportunities": agenda_setting_opportunities,
            "great_power_balance_space": great_power_balance_space
        }

    def _assess_multilateral_opportunities(self, global_data: Dict) -> List[Dict]:
        """评估多边机制参与机会"""
        international_orgs = global_data.get("international_orgs", [])
        opportunities = []

        for org in international_orgs:
            # 检查是否已参与
            current_members = org.get("members", [])
            if self.agent.state.agent_id not in current_members:
                # 评估参与收益
                benefit = self._evaluate_org_participation_benefit(org, global_data)
                if benefit > 0.5:
                    opportunities.append({
                        "org_id": org.get("org_id"),
                        "org_name": org.get("name"),
                        "participation_benefit": benefit,
                        "recommended_action": "join" if benefit > 0.7 else "observer"
                    })

        return opportunities

    def _evaluate_org_participation_benefit(self, org: Dict, global_data: Dict) -> float:
        """评估参与国际组织的收益"""
        org_type = org.get("type", "general")
        org_focus = org.get("focus", [])

        # 根据自身优势领域评估
        benefit = 0.3  # 基础参与收益

        # 检查组织焦点是否与自身优势匹配
        if "trade" in org_focus:
            benefit += 0.2
        if "development" in org_focus:
            benefit += 0.15
        if "security" in org_focus:
            benefit += 0.1

        # 检查是否有盟友参与
        members = org.get("members", [])
        relations = global_data.get("relations", {})
        friendly_members = 0
        for member in members:
            relation_key1 = f"{self.agent.state.agent_id}_{member}"
            relation_key2 = f"{member}_{self.agent.state.agent_id}"
            if relations.get(relation_key1, 0) > 0.3 or relations.get(relation_key2, 0) > 0.3:
                friendly_members += 1

        if len(members) > 0:
            benefit += (friendly_members / len(members)) * 0.2

        return min(1.0, benefit)

    def _assess_agenda_setting_opportunities(self, global_data: Dict) -> List[Dict]:
        """评估议题设置机会"""
        agenda_opportunities = []

        # 基于自身优势领域提出议题
        power_metrics = self.agent.state.power_metrics
        economic_power = power_metrics.economic_capability

        if economic_power > 100:
            agenda_opportunities.append({
                "issue": "trade_facilitation",
                "description": "促进贸易便利化与投资",
                "priority": "high",
                "estimated_impact": 0.7
            })

        if economic_power > 80:
            agenda_opportunities.append({
                "issue": "economic_development",
                "description": "推动可持续发展与减贫合作",
                "priority": "medium",
                "estimated_impact": 0.6
            })

        return agenda_opportunities

    def _assess_great_power_balance_space(self, global_data: Dict) -> float:
        """评估大国平衡空间"""
        agents = global_data.get("agents", [])
        great_powers = [
            a for a in agents
            if a.get("power_tier") in ["great_power", "superpower"]
        ]

        if len(great_powers) < 2:
            return 0.3  # 没有多极格局，平衡空间有限

        relations = global_data.get("relations", {})

        # 计算与各大国的关系
        relations_scores = []
        for gp in great_powers:
            gp_id = gp.get("agent_id")
            key1 = f"{self.agent.state.agent_id}_{gp_id}"
            key2 = f"{gp_id}_{self.agent.state.agent_id}"
            relation = max(relations.get(key1, 0), relations.get(key2, 0))
            relations_scores.append(relation)

        # 如果与所有大国关系都相对中性，平衡空间较大
        avg_relation = sum(relations_scores) / len(relations_scores)
        balance_space = 1.0 - abs(avg_relation)

        return balance_space

    def formulate_diplomatic_initiative(self, opportunity: Dict) -> Dict:
        """
        制定外交倡议

        Args:
            opportunity: 外交机会

        Returns:
            外交倡议
        """
        initiative_type = opportunity.get("type", "multilateral_engagement")

        if initiative_type == "join_organization":
            return {
                "action": "join_international_organization",
                "target_org": opportunity.get("org_id"),
                "participation_level": "full_member",
                "reasoning": f"参与{opportunity.get('org_name')}可以提升国际影响力"
            }

        elif initiative_type == "agenda_setting":
            return {
                "action": "propose_agenda_item",
                "issue": opportunity.get("issue"),
                "description": opportunity.get("description"),
                "forum": "relevant_international_forums",
                "reasoning": "在多边框架内推动有利于自身和同类国家的议题"
            }

        elif initiative_type == "balance_diplomacy":
            return {
                "action": "maintain_balanced_relations",
                "strategy": "equidistance",
                "reasoning": "在各大国间保持等距关系，保持自主性"
            }

        else:
            return {
                "action": "multilateral_cooperation",
                "focus": "dialogue_and_coordination",
                "reasoning": "积极参与多边合作，提升国际地位"
            }


class MultilateralEngagementStrategy:
    """
    多边参与策略

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(self, agent: Any):
        """
        初始化多边参与策略

        Args:
            agent: 中等强国智能体实例
        """
        self.agent = agent
        self._participation_history = []

    def identify_issue_coalitions(self, global_data: Dict) -> List[Dict]:
        """
        识别议题联盟

        Args:
            global_data: 全球数据

        Returns:
            议题联盟列表
        """
        # 找出在特定议题上利益一致的中等强国
        agents = global_data.get("agents", [])
        middle_powers = [
            a for a in agents
            if a.get("power_tier") == "middle_power" and
               a.get("agent_id") != self.agent.state.agent_id
        ]

        potential_coalitions = []

        # 基于共同议题领域寻找联盟伙伴
        my_power = self.agent.state.power_metrics
        for mp in middle_powers:
            mp_power = mp.get("power_metrics", {})
            similarity = self._calculate_interest_similarity(my_power, mp_power)

            if similarity > 0.6:
                potential_coalitions.append({
                    "partner_id": mp.get("agent_id"),
                    "partner_name": mp.get("name"),
                    "similarity_score": similarity,
                    "common_interests": self._identify_common_interests(my_power, mp_power)
                })

        # 按相似度排序
        potential_coalitions.sort(key=lambda x: x["similarity_score"], reverse=True)

        return potential_coalitions[:5]  # 返回前5个潜在伙伴

    def _calculate_interest_similarity(self, power1: Any, power2: Dict) -> float:
        """计算利益相似度"""
        # 简化实现：基于经济实力差异
        if hasattr(power1, "economic_capability"):
            eco1 = power1.economic_capability
        else:
            eco1 = power1.get("economic_capability", 100)

        eco2 = power2.get("economic_capability", 100)

        difference = abs(eco1 - eco2)
        similarity = max(0.0, 1.0 - difference / 200.0)

        return similarity

    def _identify_common_interests(self, power1: Any, power2: Dict) -> List[str]:
        """识别共同利益"""
        common_interests = []

        # 基于经济实力判断
        if hasattr(power1, "economic_capability"):
            eco1 = power1.economic_capability
        else:
            eco1 = power1.get("economic_capability", 100)

        eco2 = power2.get("economic_capability", 100)

        if eco1 > 100 and eco2 > 100:
            common_interests.append("trade_facilitation")
            common_interests.append("economic_cooperation")
        if eco1 > 80 and eco2 > 80:
            common_interests.append("sustainable_development")

        return common_interests

    def form_coalition_proposal(self, partners: List[str], issue: str) -> Dict:
        """
        组建议题联盟

        Args:
            partners: 伙伴ID列表
            issue: 议题

        Returns:
            联盟提案
        """
        return {
            "coalition_id": f"issue_coalition_{self.agent.state.agent_id}_{issue}",
            "leader": self.agent.state.agent_id,
            "members": partners + [self.agent.state.agent_id],
            "focus_issue": issue,
            "cooperation_type": "issue_specific",
            "objective": f"在{issue}议题上形成一致立场，提升话语权",
            "duration": "ad_hoc"
        }


class NicheStrategy:
    """
    利基策略 - 在特定领域建立专业优势

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(self, agent: Any):
        """
        初始化利基策略

        Args:
            agent: 中等强国智能体实例
        """
        self.agent = agent
        self._niche_areas = []

    def identify_niche_opportunities(self, global_data: Dict) -> List[Dict]:
        """
        识别利基机会领域

        Args:
            global_data: 全球数据

        Returns:
            利基机会列表
        """
        # 分析全球领域的竞争程度
        domain_competition = self._analyze_domain_competition(global_data)

        # 识别自己可以领先或发挥作用的领域
        niche_opportunities = []

        # 检查经济领域
        eco_power = self.agent.state.power_metrics.economic_capability
        if eco_power > 120 and domain_competition.get("trade", 0.9) < 0.8:
            niche_opportunities.append({
                "domain": "regional_trade_hub",
                "description": "成为区域贸易枢纽",
                "competitive_advantage": eco_power / 200.0,
                "investment_requirement": "high",
                "expected_benefit": 0.8
            })

        # 检查特定专长
        niche_opportunities.append({
            "domain": "specialized_diplomacy",
            "description": "在特定议题上建立外交专长",
            "competitive_advantage": 0.7,
            "investment_requirement": "medium",
            "expected_benefit": 0.6
        })

        niche_opportunities.append({
            "domain": "bridge_role",
            "description": "在大国与发展中国家间发挥桥梁作用",
            "competitive_advantage": 0.75,
            "investment_requirement": "medium",
            "expected_benefit": 0.7
        })

        return niche_opportunities

    def _analyze_domain_competition(self, global_data: Dict) -> Dict:
        """分析各领域的竞争程度"""
        agents = global_data.get("agents", [])
        great_powers = [
            a for a in agents
            if a.get("power_tier") in ["great_power", "superpower"]
        ]

        # 简化实现：大国参与度高意味着竞争激烈
        competition = {}

        # 假设一些通用领域的竞争情况
        competition["trade"] = 0.9 if len(great_powers) > 2 else 0.7
        competition["security"] = 0.95
        competition["environment"] = 0.6
        competition["development"] = 0.5

        return competition

    def develop_niche_position(self, niche_domain: str) -> Dict:
        """
        建立利基地位

        Args:
            niche_domain: 利基领域

        Returns:
            利基发展计划
        """
        plans = {
            "regional_trade_hub": {
                "actions": [
                    "negotiate_trade_agreements",
                    "invest_in_infrastructure",
                    "promote_investment_facilitation"
                ],
                "resource_allocation": {"economic": 0.6, "diplomatic": 0.4},
                "timeline": "medium_term"
            },
            "specialized_diplomacy": {
                "actions": [
                    "develop_expertise_in_specific_issue",
                    "participate_in_specialized_forums",
                    "publish_position_papers"
                ],
                "resource_allocation": {"diplomatic": 0.7, "research": 0.3},
                "timeline": "long_term"
            },
            "bridge_role": {
                "actions": [
                    "facilitate_dialogue_between_poles",
                    "mediate_development_projects",
                    "coordinate_aid_programs"
                ],
                "resource_allocation": {"diplomatic": 0.5, "economic": 0.5},
                "timeline": "ongoing"
            }
        }

        return plans.get(niche_domain, {})


class MiddlePowerAgent(BaseAgent):
    """
    中等强国智能体

    适用范围：中等强国 (PowerTier.MIDDLE_POWER, 0.5 < z ≤ 1.5, 约24.17%)
    不需要配置 leader_type

    特点：
    - 多边合作与平衡外交
    - 在多边机制中发挥作用
    - 推动议题设置和议程
    - 在大国间保持平衡
    - 提升国际地位和影响力

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        region: str,
        power_metrics: Any
    ):
        """
        初始化中等强国智能体

        Args:
            agent_id: 智能体唯一ID
            name: 国家名称
            region: 国家所属区域
            power_metrics: 实力指标
        """
        super().__init__(agent_id, name, region, power_metrics)

        # 策略模块将在complete_initialization中初始化
        self.diplomatic_strategy = None
        self.multilateral_strategy = None
        self.niche_strategy = None

    def complete_initialization(self) -> None:
        """完成最终初始化"""
        super().complete_initialization()

        # 初始化策略模块
        self.diplomatic_strategy = DiplomaticStrategy(self)
        self.multilateral_strategy = MultilateralEngagementStrategy(self)
        self.niche_strategy = NicheStrategy(self)

    def _get_core_preferences(self, leader_type=None) -> Dict[str, float]:
        """获取中等强国核心偏好"""
        return {
            "multilateral_cooperation": 1.0,
            "balanced_diplomacy": 0.95,
            "agenda_setting": 0.9,
            "international_status_enhancement": 0.85,
            "regional_leadership": 0.7,
            "economic_development": 0.8,
            "security_independence": 0.6,
            "autonomy_from_great_powers": 0.75
        }

    def _get_behavior_boundaries(self, leader_type=None) -> List[str]:
        """获取中等强国行为边界"""
        return [
            "通过多边机制寻求影响力",
            "在各大国间保持等距关系",
            "在特定议题上发挥专长",
            "避免过度依赖单一大国",
            "积极参与国际组织和规则制定",
            "在区域事务中发挥建设性作用",
            "灵活调整立场以适应国际形势变化"
        ]
